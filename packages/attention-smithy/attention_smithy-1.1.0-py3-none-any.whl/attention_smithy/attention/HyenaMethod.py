import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange


class HyenaOperator(nn.Module):
    """
    Implements the Hyena sequence model, replacing attention with implicit long convolutions.
    """

    def __init__(self, embedding_dim, recurrence_depth=2, filter_width=64, dropout=0.0):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.recurrence_depth = recurrence_depth
        expanded_dim = embedding_dim * (recurrence_depth + 1)

        self.input_projection = nn.Linear(embedding_dim, expanded_dim)
        self.output_projection = nn.Linear(embedding_dim, embedding_dim)

        self.short_range_convolution = nn.Conv1d(
            in_channels=expanded_dim,
            out_channels=expanded_dim,
            kernel_size=3,
            padding=2,
            groups=expanded_dim
        )

        self.filter_generator = HyenaFilter(
            output_channels=embedding_dim * (recurrence_depth - 1),
            filter_width=filter_width,
        )

        self.dropout = nn.Dropout(dropout)

    def forward(self, input_sequence__bld):
        """
        Processes an input sequence using Hyena's implicit long convolution mechanism.

        To aid in readibility, the dimensions of each intermediate value are attached to the name
            of each value. This is identified with an extra underscore as well as letters designating
            the nature of that dimension, using the below glossary as key. For example, a tensor with
            `__bld` attached indicates it is a 3D tensor of shape
            (batch_size, sequence length, embedding dimension).

        Forward pass tensor dimensions:
            - `b`: Batch size
            - `l`: Sequence length
            - `d`: Embedding dimension
            - `n`: Recurrence depth
            - `e`: Expanded embedding dimension (d * (recurrence_depth + 1))

        """
        batch_size, sequence_length, _ = input_sequence__bld.shape
        expanded_sequence__bel = self.expand_input(input_sequence__bld)
        local_context__bed = self.apply_local_convolution(expanded_sequence__bed, sequence_length)
        streams__bed = self.split_streams(local_context__bed)
        filters__led = self.filter_generator.generate_filters(sequence_length)
        processed_sequence__bed = self.apply_long_range_convolution(streams__bed, filters__led)
        combined_output__bld = self.merge_streams(processed_sequence__bed, streams__bed)
        return self.reduce_output(combined_output__bld)

    def expand_input(self, input_sequence__bld):
        return rearrange(self.input_projection(input_sequence__bld), 'b l e -> b e l')

    def apply_local_convolution(self, expanded_sequence__bed, sequence_length):
        return self.short_range_convolution(expanded_sequence__bed)[..., :sequence_length]

    def split_streams(self, processed_sequence__bed):
        return processed_sequence__bed.split(self.embedding_dim, dim=1)

    def apply_long_range_convolution(self, streams__bed, filters__led):
        output__bed = streams__bed[-1]
        for i in range(self.recurrence_depth - 1):
            output__bed = self.dropout(output__bed * streams__bed[i])
            output__bed = self.filter_generator.apply_filter(output__bed, filters__led[i])
        return output__bed

    def merge_streams(self, processed_sequence__bed, streams__bed):
        return rearrange(processed_sequence__bed * streams__bed[0], 'b d l -> b l d')

    def reduce_output(self, output_sequence__bld):
        return self.output_projection(output_sequence__bld)


class HyenaFilter(nn.Module):
    """
    Generates long-range convolution filters using an implicit function.
    """

    def __init__(self, output_channels, filter_width):
        super().__init__()
        self.output_channels = output_channels

        self.filter_network = nn.Sequential(
            nn.Linear(3, filter_width),
            nn.SiLU(),
            nn.Linear(filter_width, filter_width),
            nn.SiLU(),
            nn.Linear(filter_width, output_channels, bias=False)
        )

        self.bias = nn.Parameter(torch.randn(output_channels))

    def generate_filters(self, sequence_length):
        positions__l3 = torch.linspace(0, 1, sequence_length).unsqueeze(1).repeat(1, 3)
        filters__led = self.filter_network(positions__l3)
        return self.apply_modulation(filters__led)

    def apply_modulation(self, filters__led):
        decay__ld = torch.exp(-torch.linspace(0, 1, filters__led.shape[0]) * self.bias.abs().unsqueeze(0))
        return filters__led * decay__ld

    def apply_filter(self, input_sequence__bed, filter_weights__led):
        sequence_length = input_sequence__bed.shape[-1]
        fft_size = 2 * sequence_length
        input_fft__bed = torch.fft.rfft(input_sequence__bed, n=fft_size)
        filter_fft__led = torch.fft.rfft(filter_weights__led, n=fft_size) / fft_size
        convolved_output__bed = torch.fft.irfft(input_fft__bed * filter_fft__led, n=fft_size, norm='forward')[...,
                                :sequence_length]
        return convolved_output__bed + input_sequence__bed * self.bias.unsqueeze(-1)
