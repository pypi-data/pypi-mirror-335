# coding=utf-8
# Copyright Meta Platforms and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Data2VecVision model configuration"""


from ...configuration_utils import PretrainedConfig

from ....utils import logging


logger = logging.get_logger(__name__)


class Data2VecVisionConfig(PretrainedConfig):


    model_type = "data2vec-vision"

    def __init__(
        self,
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        hidden_act="gelu",
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        initializer_range=0.02,
        layer_norm_eps=1e-12,
        image_size=224,
        patch_size=16,
        num_channels=3,
        use_mask_token=False,
        use_absolute_position_embeddings=False,
        use_relative_position_bias=False,
        use_shared_relative_position_bias=False,
        layer_scale_init_value=0.1,
        drop_path_rate=0.1,
        use_mean_pooling=True,
        out_indices=[3, 5, 7, 11],
        pool_scales=[1, 2, 3, 6],
        use_auxiliary_head=True,
        auxiliary_loss_weight=0.4,
        auxiliary_channels=256,
        auxiliary_num_convs=1,
        auxiliary_concat_input=False,
        semantic_loss_ignore_index=255,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps

        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.use_mask_token = use_mask_token
        self.use_absolute_position_embeddings = use_absolute_position_embeddings
        self.use_relative_position_bias = use_relative_position_bias
        self.use_shared_relative_position_bias = use_shared_relative_position_bias
        self.layer_scale_init_value = layer_scale_init_value
        self.drop_path_rate = drop_path_rate
        self.use_mean_pooling = use_mean_pooling
        # decode head attributes (semantic segmentation)
        self.out_indices = out_indices
        self.pool_scales = pool_scales
        # auxiliary head attributes (semantic segmentation)
        self.use_auxiliary_head = use_auxiliary_head
        self.auxiliary_loss_weight = auxiliary_loss_weight
        self.auxiliary_channels = auxiliary_channels
        self.auxiliary_num_convs = auxiliary_num_convs
        self.auxiliary_concat_input = auxiliary_concat_input
        self.semantic_loss_ignore_index = semantic_loss_ignore_index


# Copied from transformers.models.vit.configuration_vit.ViTOnnxConfig

__all__ = ["Data2VecVisionConfig"]
