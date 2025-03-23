/**
 * Copyright 2024 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_
#define MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_

#include <functional>
#include <any>
#include <unordered_map>
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
enum class OpType {
  kMeshgrid = 0,
  kConvolutionGrad = 1,
  kReplicationPad3DGrad = 2,
  kKLDivGrad = 3,
  kRoll = 4,
  kMaxPoolWithIndices = 5,
  kScatterValue = 6,
  kAdaptiveAvgPool3DGradExt = 7,
  kInplaceMul = 8,
  kMaxPoolGradWithMask = 9,
  kInnerInplaceIndexPut = 10,
  kSpeedFusionAttention = 11,
  kNansum = 12,
  kBincountExt = 13,
  kBatchNormStats = 14,
  kBitwiseXorScalar = 15,
  kLayerNormGradExt = 16,
  kMoeTokenPermute = 17,
  kAddcdivExt = 18,
  kExpandDims = 19,
  kDiagExt = 20,
  kFlashAttentionScoreGrad = 21,
  kHShrinkGrad = 22,
  kCountNonZero = 23,
  kCumsumExt = 24,
  kFillTensor = 25,
  kMaskedFill = 26,
  kSiLUGrad = 27,
  kSqueeze = 28,
  kUniqueDim = 29,
  kInplaceUniform = 30,
  kInplaceNormal = 31,
  kSmoothL1Loss = 32,
  kInplaceHardtanh = 33,
  kSoftShrink = 34,
  kXLogYScalarOther = 35,
  kLogicalOr = 36,
  kLess = 37,
  kRandExt = 38,
  kReflectionPad2D = 39,
  kSoftMarginLoss = 40,
  kMishExt = 41,
  kSelectV2 = 42,
  kTan = 43,
  kIsInf = 44,
  kSelectExt = 45,
  kBCEWithLogitsLoss = 46,
  kNotEqual = 47,
  kBatchNormGatherStatsWithCounts = 48,
  kLogSoftmaxGrad = 49,
  kBatchNormReduceGrad = 50,
  kAcoshExt = 51,
  kInplaceFloorDivides = 52,
  kInplaceDivs = 53,
  kInnerIndex = 54,
  kMatMulExt = 55,
  kMSELossGradExt = 56,
  kMaskedSelectGrad = 57,
  kDivMod = 58,
  kLog2 = 59,
  kMinimum = 60,
  kLogSigmoidGrad = 61,
  kVar = 62,
  kBatchNormGradExt = 63,
  kNormalTensorFloat = 64,
  kBatchMatMul = 65,
  kHSigmoidGrad = 66,
  kGeLUGrad = 67,
  kAcosExt = 68,
  kConvolution = 69,
  kLogSigmoid = 70,
  kReLU = 71,
  kNeScalar = 72,
  kRandIntLike = 73,
  kLinSpaceExt = 74,
  kSplitWithSize = 75,
  kGeLU = 76,
  kSoftMarginLossGrad = 77,
  kXLogYScalarSelf = 78,
  kPReLUGrad = 79,
  kAddExt = 80,
  kUpsampleTrilinear3D = 81,
  kAddRmsNorm = 82,
  kNLLLossGrad = 83,
  kOnesLikeExt = 84,
  kNarrow = 85,
  kFmodScalar = 86,
  kUnique2 = 87,
  kInplaceScatterAdd = 88,
  kBitwiseAndTensor = 89,
  kCosh = 90,
  kReduceAll = 91,
  kFloorDiv = 92,
  kConvTranspose2D = 93,
  kScatterAddExt = 94,
  kDropoutExt = 95,
  kMv = 96,
  kLessEqual = 97,
  kTanh = 98,
  kAsinExt = 99,
  kMaxPoolGradWithIndices = 100,
  kGridSampler3DGrad = 101,
  kSeLUExt = 102,
  kSlice = 103,
  kExp = 104,
  kSeluGrad = 105,
  kSwigluGrad = 106,
  kInplaceClampTensor = 107,
  kFlattenExt = 108,
  kView = 109,
  kNormalFloatFloat = 110,
  kHistcExt = 111,
  kBinaryCrossEntropy = 112,
  kInplaceMaskedFillTensor = 113,
  kSearchSorted = 114,
  kSortExt = 115,
  kTrunc = 116,
  kNormalTensorTensor = 117,
  kBinaryCrossEntropyGrad = 118,
  kLeakyReLUGradExt = 119,
  kExpandAs = 120,
  kEluExt = 121,
  kLinalgQr = 122,
  kInplaceDivMod = 123,
  kReflectionPad3D = 124,
  kDiv = 125,
  kFullLike = 126,
  kInplaceIndexPut = 127,
  kReluGrad = 128,
  kUnstackExt = 129,
  kInplaceThreshold = 130,
  kInplaceFillDiagonal = 131,
  kCummax = 132,
  kMin = 133,
  kInplaceDivMods = 134,
  kAvgPool2DGrad = 135,
  kIndexFillTensor = 136,
  kInplaceAddmm = 137,
  kThreshold = 138,
  kSign = 139,
  kEye = 140,
  kAsStrided = 141,
  kPow = 142,
  kRandn = 143,
  kUpsampleNearest1D = 144,
  kInnerNonZero = 145,
  kProdExt = 146,
  kLogAddExp = 147,
  kBitwiseXorTensor = 148,
  kConvolutionStrGrad = 149,
  kRmsNorm = 150,
  kUpsampleBicubic2DGrad = 151,
  kEqualExt = 152,
  kFillScalar = 153,
  kMeanExt = 154,
  kHSwish = 155,
  kTExt = 156,
  kDense = 157,
  kBitwiseAndScalar = 158,
  kZerosLikeExt = 159,
  kSelect = 160,
  kMoeTokenUnpermute = 161,
  kVarMean = 162,
  kCol2ImGrad = 163,
  kAddmv = 164,
  kSoftShrinkGrad = 165,
  kMoeTokenPermuteGrad = 166,
  kGLU = 167,
  kPowScalarTensor = 168,
  kMuls = 169,
  kTanhGrad = 170,
  kInplaceIndexAddExt = 171,
  kXlogy = 172,
  kUpsampleLinear1D = 173,
  kLog10 = 174,
  kViewAs = 175,
  kReverseV2 = 176,
  kUniformExt = 177,
  kIndexAddExt = 178,
  kTake = 179,
  kInplaceDiv = 180,
  kReciprocal = 181,
  kNonZeroExt = 182,
  kThresholdGrad = 183,
  kZeros = 184,
  kSumExt = 185,
  kErf = 186,
  kBatchNormElemt = 187,
  kLayerNormExt = 188,
  kNonZero = 189,
  kReflectionPad1D = 190,
  kIsNegInf = 191,
  kKthvalue = 192,
  kGeluGradExt = 193,
  kInplaceErfinv = 194,
  kSilentCheckV3 = 195,
  kLogSoftmax = 196,
  kUpsampleBicubic2D = 197,
  kMatMul = 198,
  kAddbmm = 199,
  kClampScalar = 200,
  kMinDim = 201,
  kSliceExt = 202,
  kRepeat = 203,
  kLerpScalar = 204,
  kIndexFillScalar = 205,
  kGreater = 206,
  kStd = 207,
  kFloor = 208,
  kCos = 209,
  kUniqueConsecutive = 210,
  kAdamW = 211,
  kAllGatherMatmul = 212,
  kL1LossBackwardExt = 213,
  kTraceExt = 214,
  kSpeedFusionAttentionGrad = 215,
  kGridSampler3D = 216,
  kRsqrt = 217,
  kHSigmoid = 218,
  kNLLLoss = 219,
  kMoveTo = 220,
  kDivs = 221,
  kInplaceAddExt = 222,
  kPowTensorScalar = 223,
  kGridSampler2D = 224,
  kInplaceExp = 225,
  kGluGrad = 226,
  kConv1DExt = 227,
  kSigmoidGrad = 228,
  kBinaryCrossEntropyWithLogitsBackward = 229,
  kSoftmaxBackward = 230,
  kGcd = 231,
  kUpsampleNearest2DGrad = 232,
  kSubScalar = 233,
  kNewZeros = 234,
  kInplaceReLU = 235,
  kReplicationPad3D = 236,
  kGeluExt = 237,
  kInplaceScatterSrc = 238,
  kGroupNormGrad = 239,
  kMedianDim = 240,
  kHShrink = 241,
  kInplaceScatterValue = 242,
  kRepeatInterleaveTensor = 243,
  kMSELossExt = 244,
  kSiLU = 245,
  kErfinv = 246,
  kInplaceRandom = 247,
  kInplaceMaskedFillScalar = 248,
  kExp2 = 249,
  kReduceAny = 250,
  kRemainderTensorScalar = 251,
  kMultiScaleDeformableAttnGrad = 252,
  kInplacePut = 253,
  kGatherDGradV2 = 254,
  kFrac = 255,
  kGmmBackward = 256,
  kPReLU = 257,
  kInplaceFloor = 258,
  kAvgPool1D = 259,
  kLogicalXor = 260,
  kScatter = 261,
  kIndex = 262,
  kRandnLike = 263,
  kAddLayerNormV2 = 264,
  kSubExt = 265,
  kBroadcastTo = 266,
  kMaxUnpool2DExt = 267,
  kSoftmax = 268,
  kMax = 269,
  kUpsampleBilinear2DGrad = 270,
  kClone = 271,
  kAddScalar = 272,
  kAdaptiveAvgPool2DGradExt = 273,
  kSqrt = 274,
  kConv2DPadding = 275,
  kFFNExt = 276,
  kInplaceStopGradient = 277,
  kLogSoftmaxExt = 278,
  kNeg = 279,
  kAddmm = 280,
  kPolar = 281,
  kFlashAttentionScore = 282,
  kArgMaxWithValue = 283,
  kStackExt = 284,
  kAvgPool2D = 285,
  kGridSampler2DGrad = 286,
  kMatmulReduceScatter = 287,
  kMaskedSelect = 288,
  kUpsampleBilinear2D = 289,
  kNorm = 290,
  kTopkExt = 291,
  kAsinhExt = 292,
  kAtanExt = 293,
  kAvgPool3DExt = 294,
  kInplaceTanh = 295,
  kMm = 296,
  kBaddbmm = 297,
  kNLLLoss2dGrad = 298,
  kInplaceFloorDivide = 299,
  kAddcmulExt = 300,
  kAdaptiveMaxPool2D = 301,
  kRemainderTensorTensor = 302,
  kReflectionPad1DGrad = 303,
  kBatchNormExt = 304,
  kAtan2Ext = 305,
  kBernoulliExt = 306,
  kEmbeddingDenseBackward = 307,
  kAddLayerNormGrad = 308,
  kTriu = 309,
  kIndexSelect = 310,
  kCast = 311,
  kGenerator = 312,
  kTriangularSolve = 313,
  kAtanh = 314,
  kUpsampleTrilinear3DGrad = 315,
  kRepeatInterleaveInt = 316,
  kReflectionPad2DGrad = 317,
  kContiguous = 318,
  kConv3DPadding = 319,
  kUpsampleNearest2D = 320,
  kInplaceZero = 321,
  kOnes = 322,
  kErfc = 323,
  kCol2ImExt = 324,
  kArgMinExt = 325,
  kStdMean = 326,
  kAdaptiveMaxPool1D = 327,
  kReshape = 328,
  kChunk = 329,
  kFloorDivScalar = 330,
  kArange = 331,
  kLogAddExp2 = 332,
  kNanToNum = 333,
  kArgSort = 334,
  kLog1p = 335,
  kOuter = 336,
  kCeil = 337,
  kNewOnes = 338,
  kElu = 339,
  kRmsNormGrad = 340,
  kArgMaxExt = 341,
  kConv3DExt = 342,
  kMaxPoolWithMask = 343,
  kHSwishGrad = 344,
  kBitwiseNot = 345,
  kKLDiv = 346,
  kRandpermExt = 347,
  kTrilExt = 348,
  kMedianExt = 349,
  kOneHotExt = 350,
  kAdaptiveAvgPool2DExt = 351,
  kUpsampleLinear1DGrad = 352,
  kGmmV2Backward = 353,
  kLogSumExp = 354,
  kInplaceElu = 355,
  kReduceMax = 356,
  kSmoothL1LossGrad = 357,
  kRandInt = 358,
  kEmbedding = 359,
  kRepeatInterleaveGrad = 360,
  kFmodTensor = 361,
  kClampTensor = 362,
  kSoftplusGradExt = 363,
  kReflectionPad3DGrad = 364,
  kSinh = 365,
  kConvolutionStr = 366,
  kTypeAs = 367,
  kRemainderScalarTensor = 368,
  kRandLikeExt = 369,
  kSub = 370,
  kInplaceGroupedMatmulAdd = 371,
  kAvgPool3DGradExt = 372,
  kMaximum = 373,
  kInplaceClampScalar = 374,
  kInplaceScatterSrcReduce = 375,
  kEqual = 376,
  kAllFinite = 377,
  kSquare = 378,
  kUpsampleNearest1DGrad = 379,
  kGreaterEqualScalar = 380,
  kLinalgVectorNorm = 381,
  kInplaceSubScalar = 382,
  kMultinomialExt = 383,
  kRotaryPositionEmbeddingGrad = 384,
  kInplaceScatterValueReduce = 385,
  kBatchNormElemtGrad = 386,
  kIsFinite = 387,
  kLeakyReLUExt = 388,
  kDivMods = 389,
  kRotaryPositionEmbedding = 390,
  kIsClose = 391,
  kCumminExt = 392,
  kSigmoid = 393,
  kAdaptiveAvgPool1D = 394,
  kConstantPadND = 395,
  kNLLLoss2d = 396,
  kMishGradExt = 397,
  kCross = 398,
  kReplicationPad1D = 399,
  kTransposeExt = 400,
  kLerp = 401,
  kInplaceAddsExt = 402,
  kEluGradExt = 403,
  kMoeTokenUnpermuteGrad = 404,
  kInplaceCopy = 405,
  kDot = 406,
  kReplicationPad1DGrad = 407,
  kTranspose = 408,
  kSoftplusExt = 409,
  kAbs = 410,
  kLogicalAnd = 411,
  kSplitTensor = 412,
  kGreaterEqual = 413,
  kMultiScaleDeformableAttn = 414,
  kGroupNorm = 415,
  kSplit = 416,
  kSilentCheckV2 = 417,
  kIm2ColExt = 418,
  kIncreFlashAttention = 419,
  kLog = 420,
  kNormalFloatTensor = 421,
  kUpsampleNearest3D = 422,
  kInplaceFillTensor = 423,
  kRound = 424,
  kTile = 425,
  kInplaceMuls = 426,
  kConcat = 427,
  kCustomExt = 428,
  kReduceMin = 429,
  kReplicationPad2D = 430,
  kInplaceSubExt = 431,
  kInplaceFillScalar = 432,
  kCopy = 433,
  kTensorScatterElements = 434,
  kDropoutDoMaskExt = 435,
  kBitwiseOrTensor = 436,
  kSwiglu = 437,
  kUpsampleNearest3DGrad = 438,
  kArgMinWithValue = 439,
  kConv2DExt = 440,
  kDropoutGenMaskExt = 441,
  kInplaceLog = 442,
  kExpm1 = 443,
  kMul = 444,
  kL1LossExt = 445,
  kPromptFlashAttention = 446,
  kMatrixInverseExt = 447,
  kAdd = 448,
  kHardtanh = 449,
  kDropoutGradExt = 450,
  kLogicalNot = 451,
  kBatchMatMulExt = 452,
  kBitwiseOrScalar = 453,
  kReplicationPad2DGrad = 454,
  kSinc = 455,
  kConv1DPadding = 456,
  kGatherD = 457,
  kIdentity = 458,
  kHardtanhGrad = 459,
  kMaxDim = 460,
  kSin = 461,
  kAdaptiveAvgPool3DExt = 462,
  kQuantBatchMatmul = 463,
  kAddRmsNormQuantV2 = 464,
  kDynamicQuantExt = 465,
  kMoeComputeExpertTokens = 466,
  kGroupedMatmul = 467,
  kMatmulAllReduceAddRmsNorm = 468,
  kKVCacheScatterUpdate = 469,
  kMoeInitRouting = 470,
  kMoeInitRoutingV2 = 471,
  kGroupedMatmulV2 = 472,
  kMoeFinalizeRouting = 473,
  kFusedInferAttentionScore = 474,
  kQuantV2 = 475,
  kWeightQuantBatchMatmul = 476,
  kGroupedMatmulV4 = 477,
  kMoeGatingTopKSoftmax = 478,
  kPixelShuffle = 479,
};

using MeshgridGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using ConvolutionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using ReplicationPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using KLDivGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using RollGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using MaxPoolWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using ScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using AdaptiveAvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxPoolGradWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using InnerInplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using SpeedFusionAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using NansumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using BincountExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using BatchNormStatsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using BitwiseXorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using LayerNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MoeTokenPermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using AddcdivExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ExpandDimsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using DiagExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using FlashAttentionScoreGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using HShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using CountNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using CumsumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using FillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MaskedFillGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SiLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SqueezeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using UniqueDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceUniformGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceNormalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SmoothL1LossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceHardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SoftShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using XLogYScalarOtherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using LogicalOrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LessGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReflectionPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SoftMarginLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MishExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SelectV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SelectExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using BCEWithLogitsLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using NotEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchNormGatherStatsWithCountsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using LogSoftmaxGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using BatchNormReduceGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AcoshExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceFloorDividesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceDivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InnerIndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MSELossGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MaskedSelectGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using Log2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MinimumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using VarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &)>;
using NormalTensorFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchMatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using HSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GeLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AcosExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvolutionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using LogSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NeScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using RandIntLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LinSpaceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SplitWithSizeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using GeLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SoftMarginLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using XLogYScalarSelfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using PReLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using UpsampleTrilinear3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using AddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using NLLLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using OnesLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NarrowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using FmodScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using Unique2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceScatterAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseAndTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CoshGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReduceAllGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using FloorDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvTranspose2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using ScatterAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DropoutExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LessEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AsinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxPoolGradWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using GridSampler3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using SeLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SliceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using ExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SeluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SwigluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using FlattenExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using NormalFloatFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HistcExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using BinaryCrossEntropyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using InplaceMaskedFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SearchSortedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SortExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using TruncGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormalTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BinaryCrossEntropyGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using LeakyReLUGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using ExpandAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using LinalgQrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceDivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReflectionPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using DivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FullLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using ReluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UnstackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceFillDiagonalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using CummaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceDivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AvgPool2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using IndexFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceAddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using SignGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EyeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AsStridedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using PowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using UpsampleNearest1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InnerNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ProdExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogAddExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseXorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvolutionStrGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using RmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using UpsampleBicubic2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using EqualExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MeanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using HSwishGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DenseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using BitwiseAndScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ZerosLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MoeTokenUnpermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using VarMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using Col2ImGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using AddmvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SoftShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using MoeTokenPermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using PowScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using TanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceIndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using XlogyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleLinear1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using Log10GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ViewAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReverseV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using UniformExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using TakeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReciprocalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NonZeroExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ThresholdGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using ZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ErfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchNormElemtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using LayerNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using NonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReflectionPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using IsNegInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using KthvalueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GeluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SilentCheckV3GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using LogSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleBicubic2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using MatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using MinDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SliceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RepeatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using LerpScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using IndexFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using GreaterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using StdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using FloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UniqueConsecutiveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AdamWGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AllGatherMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using L1LossBackwardExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using TraceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SpeedFusionAttentionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using GridSampler3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using RsqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NLLLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoveToGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::BoolImmPtr &)>;
using DivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using PowTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using GridSampler2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using Conv1DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BinaryCrossEntropyWithLogitsBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using SoftmaxBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using GcdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using NewZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReplicationPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using GeluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceScatterSrcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GroupNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MedianDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using HShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using RepeatInterleaveTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MSELossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using SiLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceRandomGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceMaskedFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using Exp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReduceAnyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using RemainderTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using MultiScaleDeformableAttnGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplacePutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using GatherDGradV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FracGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GmmBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using PReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceFloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using LogicalXorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using IndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using RandnLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AddLayerNormV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using SubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using BroadcastToGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MaxUnpool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleBilinear2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using CloneGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AdaptiveAvgPool2DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv2DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using FFNExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceStopGradientGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogSoftmaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NegGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using PolarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FlashAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ArgMaxWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using StackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using AvgPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using GridSampler2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using MatmulReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MaskedSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleBilinear2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using NormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using TopkExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AsinhExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AtanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceTanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BaddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using NLLLoss2dGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceFloorDivideGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddcmulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using AdaptiveMaxPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using RemainderTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReflectionPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using BatchNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using Atan2ExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BernoulliExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EmbeddingDenseBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using AddLayerNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TriuGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using IndexSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CastGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using GeneratorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using TriangularSolveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleTrilinear3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using RepeatInterleaveIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReflectionPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ContiguousGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv3DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleNearest2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using OnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ErfcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Col2ImExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using ArgMinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using StdMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AdaptiveMaxPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ReshapeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ChunkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using FloorDivScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ArangeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogAddExp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NanToNumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &)>;
using ArgSortGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using Log1pGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using OuterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CeilGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NewOnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using EluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using RmsNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ArgMaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using Conv3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using MaxPoolWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using HSwishGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using KLDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using RandpermExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using TrilExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MedianExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using OneHotExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using AdaptiveAvgPool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using UpsampleLinear1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using GmmV2BackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using LogSumExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using InplaceEluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using ReduceMaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using SmoothL1LossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RandIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using EmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using RepeatInterleaveGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using FmodTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using SoftplusGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ReflectionPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SinhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvolutionStrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using TypeAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RemainderScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SubGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceGroupedMatmulAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MaximumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using InplaceScatterSrcReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using EqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AllFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using SquareGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using GreaterEqualScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using LinalgVectorNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceSubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MultinomialExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RotaryPositionEmbeddingGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using InplaceScatterValueReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using BatchNormElemtGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LeakyReLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using DivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RotaryPositionEmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using IsCloseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using CumminExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using SigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AdaptiveAvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ConstantPadNDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &)>;
using NLLLoss2dGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MishGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CrossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using ReplicationPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using TransposeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using LerpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceAddsExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using EluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using MoeTokenUnpermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceCopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReplicationPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using TransposeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SoftplusExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AbsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogicalAndGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SplitTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GreaterEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MultiScaleDeformableAttnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GroupNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using SplitGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using SilentCheckV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using Im2ColExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using IncreFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using LogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormalFloatTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RoundGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using TileGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceMulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ConcatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using CustomExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using ReduceMinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using ReplicationPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceSubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using CopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TensorScatterElementsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using DropoutDoMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using BitwiseOrTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SwigluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleNearest3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ArgMinWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using Conv2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using DropoutGenMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceLogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Expm1GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using L1LossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using PromptFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MatrixInverseExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using DropoutGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using LogicalNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchMatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseOrScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ReplicationPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SincGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv1DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using GatherDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IdentityGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HardtanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MaxDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AdaptiveAvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using QuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using AddRmsNormQuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using DynamicQuantExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using MoeComputeExpertTokensGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MatmulAllReduceAddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using KVCacheScatterUpdateGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GroupedMatmulV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeFinalizeRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using FusedInferAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using QuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using WeightQuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulV4GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeGatingTopKSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using PixelShuffleGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;

struct OpsAutoGradRegisters {
  MeshgridGradFunc MeshgridGradFuncObj;
  ConvolutionGradGradFunc ConvolutionGradGradFuncObj;
  ReplicationPad3DGradGradFunc ReplicationPad3DGradGradFuncObj;
  KLDivGradGradFunc KLDivGradGradFuncObj;
  RollGradFunc RollGradFuncObj;
  MaxPoolWithIndicesGradFunc MaxPoolWithIndicesGradFuncObj;
  ScatterValueGradFunc ScatterValueGradFuncObj;
  AdaptiveAvgPool3DGradExtGradFunc AdaptiveAvgPool3DGradExtGradFuncObj;
  InplaceMulGradFunc InplaceMulGradFuncObj;
  MaxPoolGradWithMaskGradFunc MaxPoolGradWithMaskGradFuncObj;
  InnerInplaceIndexPutGradFunc InnerInplaceIndexPutGradFuncObj;
  SpeedFusionAttentionGradFunc SpeedFusionAttentionGradFuncObj;
  NansumGradFunc NansumGradFuncObj;
  BincountExtGradFunc BincountExtGradFuncObj;
  BatchNormStatsGradFunc BatchNormStatsGradFuncObj;
  BitwiseXorScalarGradFunc BitwiseXorScalarGradFuncObj;
  LayerNormGradExtGradFunc LayerNormGradExtGradFuncObj;
  MoeTokenPermuteGradFunc MoeTokenPermuteGradFuncObj;
  AddcdivExtGradFunc AddcdivExtGradFuncObj;
  ExpandDimsGradFunc ExpandDimsGradFuncObj;
  DiagExtGradFunc DiagExtGradFuncObj;
  FlashAttentionScoreGradGradFunc FlashAttentionScoreGradGradFuncObj;
  HShrinkGradGradFunc HShrinkGradGradFuncObj;
  CountNonZeroGradFunc CountNonZeroGradFuncObj;
  CumsumExtGradFunc CumsumExtGradFuncObj;
  FillTensorGradFunc FillTensorGradFuncObj;
  MaskedFillGradFunc MaskedFillGradFuncObj;
  SiLUGradGradFunc SiLUGradGradFuncObj;
  SqueezeGradFunc SqueezeGradFuncObj;
  UniqueDimGradFunc UniqueDimGradFuncObj;
  InplaceUniformGradFunc InplaceUniformGradFuncObj;
  InplaceNormalGradFunc InplaceNormalGradFuncObj;
  SmoothL1LossGradFunc SmoothL1LossGradFuncObj;
  InplaceHardtanhGradFunc InplaceHardtanhGradFuncObj;
  SoftShrinkGradFunc SoftShrinkGradFuncObj;
  XLogYScalarOtherGradFunc XLogYScalarOtherGradFuncObj;
  LogicalOrGradFunc LogicalOrGradFuncObj;
  LessGradFunc LessGradFuncObj;
  RandExtGradFunc RandExtGradFuncObj;
  ReflectionPad2DGradFunc ReflectionPad2DGradFuncObj;
  SoftMarginLossGradFunc SoftMarginLossGradFuncObj;
  MishExtGradFunc MishExtGradFuncObj;
  SelectV2GradFunc SelectV2GradFuncObj;
  TanGradFunc TanGradFuncObj;
  IsInfGradFunc IsInfGradFuncObj;
  SelectExtGradFunc SelectExtGradFuncObj;
  BCEWithLogitsLossGradFunc BCEWithLogitsLossGradFuncObj;
  NotEqualGradFunc NotEqualGradFuncObj;
  BatchNormGatherStatsWithCountsGradFunc BatchNormGatherStatsWithCountsGradFuncObj;
  LogSoftmaxGradGradFunc LogSoftmaxGradGradFuncObj;
  BatchNormReduceGradGradFunc BatchNormReduceGradGradFuncObj;
  AcoshExtGradFunc AcoshExtGradFuncObj;
  InplaceFloorDividesGradFunc InplaceFloorDividesGradFuncObj;
  InplaceDivsGradFunc InplaceDivsGradFuncObj;
  InnerIndexGradFunc InnerIndexGradFuncObj;
  MatMulExtGradFunc MatMulExtGradFuncObj;
  MSELossGradExtGradFunc MSELossGradExtGradFuncObj;
  MaskedSelectGradGradFunc MaskedSelectGradGradFuncObj;
  DivModGradFunc DivModGradFuncObj;
  Log2GradFunc Log2GradFuncObj;
  MinimumGradFunc MinimumGradFuncObj;
  LogSigmoidGradGradFunc LogSigmoidGradGradFuncObj;
  VarGradFunc VarGradFuncObj;
  BatchNormGradExtGradFunc BatchNormGradExtGradFuncObj;
  NormalTensorFloatGradFunc NormalTensorFloatGradFuncObj;
  BatchMatMulGradFunc BatchMatMulGradFuncObj;
  HSigmoidGradGradFunc HSigmoidGradGradFuncObj;
  GeLUGradGradFunc GeLUGradGradFuncObj;
  AcosExtGradFunc AcosExtGradFuncObj;
  ConvolutionGradFunc ConvolutionGradFuncObj;
  LogSigmoidGradFunc LogSigmoidGradFuncObj;
  ReLUGradFunc ReLUGradFuncObj;
  NeScalarGradFunc NeScalarGradFuncObj;
  RandIntLikeGradFunc RandIntLikeGradFuncObj;
  LinSpaceExtGradFunc LinSpaceExtGradFuncObj;
  SplitWithSizeGradFunc SplitWithSizeGradFuncObj;
  GeLUGradFunc GeLUGradFuncObj;
  SoftMarginLossGradGradFunc SoftMarginLossGradGradFuncObj;
  XLogYScalarSelfGradFunc XLogYScalarSelfGradFuncObj;
  PReLUGradGradFunc PReLUGradGradFuncObj;
  AddExtGradFunc AddExtGradFuncObj;
  UpsampleTrilinear3DGradFunc UpsampleTrilinear3DGradFuncObj;
  AddRmsNormGradFunc AddRmsNormGradFuncObj;
  NLLLossGradGradFunc NLLLossGradGradFuncObj;
  OnesLikeExtGradFunc OnesLikeExtGradFuncObj;
  NarrowGradFunc NarrowGradFuncObj;
  FmodScalarGradFunc FmodScalarGradFuncObj;
  Unique2GradFunc Unique2GradFuncObj;
  InplaceScatterAddGradFunc InplaceScatterAddGradFuncObj;
  BitwiseAndTensorGradFunc BitwiseAndTensorGradFuncObj;
  CoshGradFunc CoshGradFuncObj;
  ReduceAllGradFunc ReduceAllGradFuncObj;
  FloorDivGradFunc FloorDivGradFuncObj;
  ConvTranspose2DGradFunc ConvTranspose2DGradFuncObj;
  ScatterAddExtGradFunc ScatterAddExtGradFuncObj;
  DropoutExtGradFunc DropoutExtGradFuncObj;
  MvGradFunc MvGradFuncObj;
  LessEqualGradFunc LessEqualGradFuncObj;
  TanhGradFunc TanhGradFuncObj;
  AsinExtGradFunc AsinExtGradFuncObj;
  MaxPoolGradWithIndicesGradFunc MaxPoolGradWithIndicesGradFuncObj;
  GridSampler3DGradGradFunc GridSampler3DGradGradFuncObj;
  SeLUExtGradFunc SeLUExtGradFuncObj;
  SliceGradFunc SliceGradFuncObj;
  ExpGradFunc ExpGradFuncObj;
  SeluGradGradFunc SeluGradGradFuncObj;
  SwigluGradGradFunc SwigluGradGradFuncObj;
  InplaceClampTensorGradFunc InplaceClampTensorGradFuncObj;
  FlattenExtGradFunc FlattenExtGradFuncObj;
  ViewGradFunc ViewGradFuncObj;
  NormalFloatFloatGradFunc NormalFloatFloatGradFuncObj;
  HistcExtGradFunc HistcExtGradFuncObj;
  BinaryCrossEntropyGradFunc BinaryCrossEntropyGradFuncObj;
  InplaceMaskedFillTensorGradFunc InplaceMaskedFillTensorGradFuncObj;
  SearchSortedGradFunc SearchSortedGradFuncObj;
  SortExtGradFunc SortExtGradFuncObj;
  TruncGradFunc TruncGradFuncObj;
  NormalTensorTensorGradFunc NormalTensorTensorGradFuncObj;
  BinaryCrossEntropyGradGradFunc BinaryCrossEntropyGradGradFuncObj;
  LeakyReLUGradExtGradFunc LeakyReLUGradExtGradFuncObj;
  ExpandAsGradFunc ExpandAsGradFuncObj;
  EluExtGradFunc EluExtGradFuncObj;
  LinalgQrGradFunc LinalgQrGradFuncObj;
  InplaceDivModGradFunc InplaceDivModGradFuncObj;
  ReflectionPad3DGradFunc ReflectionPad3DGradFuncObj;
  DivGradFunc DivGradFuncObj;
  FullLikeGradFunc FullLikeGradFuncObj;
  InplaceIndexPutGradFunc InplaceIndexPutGradFuncObj;
  ReluGradGradFunc ReluGradGradFuncObj;
  UnstackExtGradFunc UnstackExtGradFuncObj;
  InplaceThresholdGradFunc InplaceThresholdGradFuncObj;
  InplaceFillDiagonalGradFunc InplaceFillDiagonalGradFuncObj;
  CummaxGradFunc CummaxGradFuncObj;
  MinGradFunc MinGradFuncObj;
  InplaceDivModsGradFunc InplaceDivModsGradFuncObj;
  AvgPool2DGradGradFunc AvgPool2DGradGradFuncObj;
  IndexFillTensorGradFunc IndexFillTensorGradFuncObj;
  InplaceAddmmGradFunc InplaceAddmmGradFuncObj;
  ThresholdGradFunc ThresholdGradFuncObj;
  SignGradFunc SignGradFuncObj;
  EyeGradFunc EyeGradFuncObj;
  AsStridedGradFunc AsStridedGradFuncObj;
  PowGradFunc PowGradFuncObj;
  RandnGradFunc RandnGradFuncObj;
  UpsampleNearest1DGradFunc UpsampleNearest1DGradFuncObj;
  InnerNonZeroGradFunc InnerNonZeroGradFuncObj;
  ProdExtGradFunc ProdExtGradFuncObj;
  LogAddExpGradFunc LogAddExpGradFuncObj;
  BitwiseXorTensorGradFunc BitwiseXorTensorGradFuncObj;
  ConvolutionStrGradGradFunc ConvolutionStrGradGradFuncObj;
  RmsNormGradFunc RmsNormGradFuncObj;
  UpsampleBicubic2DGradGradFunc UpsampleBicubic2DGradGradFuncObj;
  EqualExtGradFunc EqualExtGradFuncObj;
  FillScalarGradFunc FillScalarGradFuncObj;
  MeanExtGradFunc MeanExtGradFuncObj;
  HSwishGradFunc HSwishGradFuncObj;
  TExtGradFunc TExtGradFuncObj;
  DenseGradFunc DenseGradFuncObj;
  BitwiseAndScalarGradFunc BitwiseAndScalarGradFuncObj;
  ZerosLikeExtGradFunc ZerosLikeExtGradFuncObj;
  SelectGradFunc SelectGradFuncObj;
  MoeTokenUnpermuteGradFunc MoeTokenUnpermuteGradFuncObj;
  VarMeanGradFunc VarMeanGradFuncObj;
  Col2ImGradGradFunc Col2ImGradGradFuncObj;
  AddmvGradFunc AddmvGradFuncObj;
  SoftShrinkGradGradFunc SoftShrinkGradGradFuncObj;
  MoeTokenPermuteGradGradFunc MoeTokenPermuteGradGradFuncObj;
  GLUGradFunc GLUGradFuncObj;
  PowScalarTensorGradFunc PowScalarTensorGradFuncObj;
  MulsGradFunc MulsGradFuncObj;
  TanhGradGradFunc TanhGradGradFuncObj;
  InplaceIndexAddExtGradFunc InplaceIndexAddExtGradFuncObj;
  XlogyGradFunc XlogyGradFuncObj;
  UpsampleLinear1DGradFunc UpsampleLinear1DGradFuncObj;
  Log10GradFunc Log10GradFuncObj;
  ViewAsGradFunc ViewAsGradFuncObj;
  ReverseV2GradFunc ReverseV2GradFuncObj;
  UniformExtGradFunc UniformExtGradFuncObj;
  IndexAddExtGradFunc IndexAddExtGradFuncObj;
  TakeGradFunc TakeGradFuncObj;
  InplaceDivGradFunc InplaceDivGradFuncObj;
  ReciprocalGradFunc ReciprocalGradFuncObj;
  NonZeroExtGradFunc NonZeroExtGradFuncObj;
  ThresholdGradGradFunc ThresholdGradGradFuncObj;
  ZerosGradFunc ZerosGradFuncObj;
  SumExtGradFunc SumExtGradFuncObj;
  ErfGradFunc ErfGradFuncObj;
  BatchNormElemtGradFunc BatchNormElemtGradFuncObj;
  LayerNormExtGradFunc LayerNormExtGradFuncObj;
  NonZeroGradFunc NonZeroGradFuncObj;
  ReflectionPad1DGradFunc ReflectionPad1DGradFuncObj;
  IsNegInfGradFunc IsNegInfGradFuncObj;
  KthvalueGradFunc KthvalueGradFuncObj;
  GeluGradExtGradFunc GeluGradExtGradFuncObj;
  InplaceErfinvGradFunc InplaceErfinvGradFuncObj;
  SilentCheckV3GradFunc SilentCheckV3GradFuncObj;
  LogSoftmaxGradFunc LogSoftmaxGradFuncObj;
  UpsampleBicubic2DGradFunc UpsampleBicubic2DGradFuncObj;
  MatMulGradFunc MatMulGradFuncObj;
  AddbmmGradFunc AddbmmGradFuncObj;
  ClampScalarGradFunc ClampScalarGradFuncObj;
  MinDimGradFunc MinDimGradFuncObj;
  SliceExtGradFunc SliceExtGradFuncObj;
  RepeatGradFunc RepeatGradFuncObj;
  LerpScalarGradFunc LerpScalarGradFuncObj;
  IndexFillScalarGradFunc IndexFillScalarGradFuncObj;
  GreaterGradFunc GreaterGradFuncObj;
  StdGradFunc StdGradFuncObj;
  FloorGradFunc FloorGradFuncObj;
  CosGradFunc CosGradFuncObj;
  UniqueConsecutiveGradFunc UniqueConsecutiveGradFuncObj;
  AdamWGradFunc AdamWGradFuncObj;
  AllGatherMatmulGradFunc AllGatherMatmulGradFuncObj;
  L1LossBackwardExtGradFunc L1LossBackwardExtGradFuncObj;
  TraceExtGradFunc TraceExtGradFuncObj;
  SpeedFusionAttentionGradGradFunc SpeedFusionAttentionGradGradFuncObj;
  GridSampler3DGradFunc GridSampler3DGradFuncObj;
  RsqrtGradFunc RsqrtGradFuncObj;
  HSigmoidGradFunc HSigmoidGradFuncObj;
  NLLLossGradFunc NLLLossGradFuncObj;
  MoveToGradFunc MoveToGradFuncObj;
  DivsGradFunc DivsGradFuncObj;
  InplaceAddExtGradFunc InplaceAddExtGradFuncObj;
  PowTensorScalarGradFunc PowTensorScalarGradFuncObj;
  GridSampler2DGradFunc GridSampler2DGradFuncObj;
  InplaceExpGradFunc InplaceExpGradFuncObj;
  GluGradGradFunc GluGradGradFuncObj;
  Conv1DExtGradFunc Conv1DExtGradFuncObj;
  SigmoidGradGradFunc SigmoidGradGradFuncObj;
  BinaryCrossEntropyWithLogitsBackwardGradFunc BinaryCrossEntropyWithLogitsBackwardGradFuncObj;
  SoftmaxBackwardGradFunc SoftmaxBackwardGradFuncObj;
  GcdGradFunc GcdGradFuncObj;
  UpsampleNearest2DGradGradFunc UpsampleNearest2DGradGradFuncObj;
  SubScalarGradFunc SubScalarGradFuncObj;
  NewZerosGradFunc NewZerosGradFuncObj;
  InplaceReLUGradFunc InplaceReLUGradFuncObj;
  ReplicationPad3DGradFunc ReplicationPad3DGradFuncObj;
  GeluExtGradFunc GeluExtGradFuncObj;
  InplaceScatterSrcGradFunc InplaceScatterSrcGradFuncObj;
  GroupNormGradGradFunc GroupNormGradGradFuncObj;
  MedianDimGradFunc MedianDimGradFuncObj;
  HShrinkGradFunc HShrinkGradFuncObj;
  InplaceScatterValueGradFunc InplaceScatterValueGradFuncObj;
  RepeatInterleaveTensorGradFunc RepeatInterleaveTensorGradFuncObj;
  MSELossExtGradFunc MSELossExtGradFuncObj;
  SiLUGradFunc SiLUGradFuncObj;
  ErfinvGradFunc ErfinvGradFuncObj;
  InplaceRandomGradFunc InplaceRandomGradFuncObj;
  InplaceMaskedFillScalarGradFunc InplaceMaskedFillScalarGradFuncObj;
  Exp2GradFunc Exp2GradFuncObj;
  ReduceAnyGradFunc ReduceAnyGradFuncObj;
  RemainderTensorScalarGradFunc RemainderTensorScalarGradFuncObj;
  MultiScaleDeformableAttnGradGradFunc MultiScaleDeformableAttnGradGradFuncObj;
  InplacePutGradFunc InplacePutGradFuncObj;
  GatherDGradV2GradFunc GatherDGradV2GradFuncObj;
  FracGradFunc FracGradFuncObj;
  GmmBackwardGradFunc GmmBackwardGradFuncObj;
  PReLUGradFunc PReLUGradFuncObj;
  InplaceFloorGradFunc InplaceFloorGradFuncObj;
  AvgPool1DGradFunc AvgPool1DGradFuncObj;
  LogicalXorGradFunc LogicalXorGradFuncObj;
  ScatterGradFunc ScatterGradFuncObj;
  IndexGradFunc IndexGradFuncObj;
  RandnLikeGradFunc RandnLikeGradFuncObj;
  AddLayerNormV2GradFunc AddLayerNormV2GradFuncObj;
  SubExtGradFunc SubExtGradFuncObj;
  BroadcastToGradFunc BroadcastToGradFuncObj;
  MaxUnpool2DExtGradFunc MaxUnpool2DExtGradFuncObj;
  SoftmaxGradFunc SoftmaxGradFuncObj;
  MaxGradFunc MaxGradFuncObj;
  UpsampleBilinear2DGradGradFunc UpsampleBilinear2DGradGradFuncObj;
  CloneGradFunc CloneGradFuncObj;
  AddScalarGradFunc AddScalarGradFuncObj;
  AdaptiveAvgPool2DGradExtGradFunc AdaptiveAvgPool2DGradExtGradFuncObj;
  SqrtGradFunc SqrtGradFuncObj;
  Conv2DPaddingGradFunc Conv2DPaddingGradFuncObj;
  FFNExtGradFunc FFNExtGradFuncObj;
  InplaceStopGradientGradFunc InplaceStopGradientGradFuncObj;
  LogSoftmaxExtGradFunc LogSoftmaxExtGradFuncObj;
  NegGradFunc NegGradFuncObj;
  AddmmGradFunc AddmmGradFuncObj;
  PolarGradFunc PolarGradFuncObj;
  FlashAttentionScoreGradFunc FlashAttentionScoreGradFuncObj;
  ArgMaxWithValueGradFunc ArgMaxWithValueGradFuncObj;
  StackExtGradFunc StackExtGradFuncObj;
  AvgPool2DGradFunc AvgPool2DGradFuncObj;
  GridSampler2DGradGradFunc GridSampler2DGradGradFuncObj;
  MatmulReduceScatterGradFunc MatmulReduceScatterGradFuncObj;
  MaskedSelectGradFunc MaskedSelectGradFuncObj;
  UpsampleBilinear2DGradFunc UpsampleBilinear2DGradFuncObj;
  NormGradFunc NormGradFuncObj;
  TopkExtGradFunc TopkExtGradFuncObj;
  AsinhExtGradFunc AsinhExtGradFuncObj;
  AtanExtGradFunc AtanExtGradFuncObj;
  AvgPool3DExtGradFunc AvgPool3DExtGradFuncObj;
  InplaceTanhGradFunc InplaceTanhGradFuncObj;
  MmGradFunc MmGradFuncObj;
  BaddbmmGradFunc BaddbmmGradFuncObj;
  NLLLoss2dGradGradFunc NLLLoss2dGradGradFuncObj;
  InplaceFloorDivideGradFunc InplaceFloorDivideGradFuncObj;
  AddcmulExtGradFunc AddcmulExtGradFuncObj;
  AdaptiveMaxPool2DGradFunc AdaptiveMaxPool2DGradFuncObj;
  RemainderTensorTensorGradFunc RemainderTensorTensorGradFuncObj;
  ReflectionPad1DGradGradFunc ReflectionPad1DGradGradFuncObj;
  BatchNormExtGradFunc BatchNormExtGradFuncObj;
  Atan2ExtGradFunc Atan2ExtGradFuncObj;
  BernoulliExtGradFunc BernoulliExtGradFuncObj;
  EmbeddingDenseBackwardGradFunc EmbeddingDenseBackwardGradFuncObj;
  AddLayerNormGradGradFunc AddLayerNormGradGradFuncObj;
  TriuGradFunc TriuGradFuncObj;
  IndexSelectGradFunc IndexSelectGradFuncObj;
  CastGradFunc CastGradFuncObj;
  GeneratorGradFunc GeneratorGradFuncObj;
  TriangularSolveGradFunc TriangularSolveGradFuncObj;
  AtanhGradFunc AtanhGradFuncObj;
  UpsampleTrilinear3DGradGradFunc UpsampleTrilinear3DGradGradFuncObj;
  RepeatInterleaveIntGradFunc RepeatInterleaveIntGradFuncObj;
  ReflectionPad2DGradGradFunc ReflectionPad2DGradGradFuncObj;
  ContiguousGradFunc ContiguousGradFuncObj;
  Conv3DPaddingGradFunc Conv3DPaddingGradFuncObj;
  UpsampleNearest2DGradFunc UpsampleNearest2DGradFuncObj;
  InplaceZeroGradFunc InplaceZeroGradFuncObj;
  OnesGradFunc OnesGradFuncObj;
  ErfcGradFunc ErfcGradFuncObj;
  Col2ImExtGradFunc Col2ImExtGradFuncObj;
  ArgMinExtGradFunc ArgMinExtGradFuncObj;
  StdMeanGradFunc StdMeanGradFuncObj;
  AdaptiveMaxPool1DGradFunc AdaptiveMaxPool1DGradFuncObj;
  ReshapeGradFunc ReshapeGradFuncObj;
  ChunkGradFunc ChunkGradFuncObj;
  FloorDivScalarGradFunc FloorDivScalarGradFuncObj;
  ArangeGradFunc ArangeGradFuncObj;
  LogAddExp2GradFunc LogAddExp2GradFuncObj;
  NanToNumGradFunc NanToNumGradFuncObj;
  ArgSortGradFunc ArgSortGradFuncObj;
  Log1pGradFunc Log1pGradFuncObj;
  OuterGradFunc OuterGradFuncObj;
  CeilGradFunc CeilGradFuncObj;
  NewOnesGradFunc NewOnesGradFuncObj;
  EluGradFunc EluGradFuncObj;
  RmsNormGradGradFunc RmsNormGradGradFuncObj;
  ArgMaxExtGradFunc ArgMaxExtGradFuncObj;
  Conv3DExtGradFunc Conv3DExtGradFuncObj;
  MaxPoolWithMaskGradFunc MaxPoolWithMaskGradFuncObj;
  HSwishGradGradFunc HSwishGradGradFuncObj;
  BitwiseNotGradFunc BitwiseNotGradFuncObj;
  KLDivGradFunc KLDivGradFuncObj;
  RandpermExtGradFunc RandpermExtGradFuncObj;
  TrilExtGradFunc TrilExtGradFuncObj;
  MedianExtGradFunc MedianExtGradFuncObj;
  OneHotExtGradFunc OneHotExtGradFuncObj;
  AdaptiveAvgPool2DExtGradFunc AdaptiveAvgPool2DExtGradFuncObj;
  UpsampleLinear1DGradGradFunc UpsampleLinear1DGradGradFuncObj;
  GmmV2BackwardGradFunc GmmV2BackwardGradFuncObj;
  LogSumExpGradFunc LogSumExpGradFuncObj;
  InplaceEluGradFunc InplaceEluGradFuncObj;
  ReduceMaxGradFunc ReduceMaxGradFuncObj;
  SmoothL1LossGradGradFunc SmoothL1LossGradGradFuncObj;
  RandIntGradFunc RandIntGradFuncObj;
  EmbeddingGradFunc EmbeddingGradFuncObj;
  RepeatInterleaveGradGradFunc RepeatInterleaveGradGradFuncObj;
  FmodTensorGradFunc FmodTensorGradFuncObj;
  ClampTensorGradFunc ClampTensorGradFuncObj;
  SoftplusGradExtGradFunc SoftplusGradExtGradFuncObj;
  ReflectionPad3DGradGradFunc ReflectionPad3DGradGradFuncObj;
  SinhGradFunc SinhGradFuncObj;
  ConvolutionStrGradFunc ConvolutionStrGradFuncObj;
  TypeAsGradFunc TypeAsGradFuncObj;
  RemainderScalarTensorGradFunc RemainderScalarTensorGradFuncObj;
  RandLikeExtGradFunc RandLikeExtGradFuncObj;
  SubGradFunc SubGradFuncObj;
  InplaceGroupedMatmulAddGradFunc InplaceGroupedMatmulAddGradFuncObj;
  AvgPool3DGradExtGradFunc AvgPool3DGradExtGradFuncObj;
  MaximumGradFunc MaximumGradFuncObj;
  InplaceClampScalarGradFunc InplaceClampScalarGradFuncObj;
  InplaceScatterSrcReduceGradFunc InplaceScatterSrcReduceGradFuncObj;
  EqualGradFunc EqualGradFuncObj;
  AllFiniteGradFunc AllFiniteGradFuncObj;
  SquareGradFunc SquareGradFuncObj;
  UpsampleNearest1DGradGradFunc UpsampleNearest1DGradGradFuncObj;
  GreaterEqualScalarGradFunc GreaterEqualScalarGradFuncObj;
  LinalgVectorNormGradFunc LinalgVectorNormGradFuncObj;
  InplaceSubScalarGradFunc InplaceSubScalarGradFuncObj;
  MultinomialExtGradFunc MultinomialExtGradFuncObj;
  RotaryPositionEmbeddingGradGradFunc RotaryPositionEmbeddingGradGradFuncObj;
  InplaceScatterValueReduceGradFunc InplaceScatterValueReduceGradFuncObj;
  BatchNormElemtGradGradFunc BatchNormElemtGradGradFuncObj;
  IsFiniteGradFunc IsFiniteGradFuncObj;
  LeakyReLUExtGradFunc LeakyReLUExtGradFuncObj;
  DivModsGradFunc DivModsGradFuncObj;
  RotaryPositionEmbeddingGradFunc RotaryPositionEmbeddingGradFuncObj;
  IsCloseGradFunc IsCloseGradFuncObj;
  CumminExtGradFunc CumminExtGradFuncObj;
  SigmoidGradFunc SigmoidGradFuncObj;
  AdaptiveAvgPool1DGradFunc AdaptiveAvgPool1DGradFuncObj;
  ConstantPadNDGradFunc ConstantPadNDGradFuncObj;
  NLLLoss2dGradFunc NLLLoss2dGradFuncObj;
  MishGradExtGradFunc MishGradExtGradFuncObj;
  CrossGradFunc CrossGradFuncObj;
  ReplicationPad1DGradFunc ReplicationPad1DGradFuncObj;
  TransposeExtGradFunc TransposeExtGradFuncObj;
  LerpGradFunc LerpGradFuncObj;
  InplaceAddsExtGradFunc InplaceAddsExtGradFuncObj;
  EluGradExtGradFunc EluGradExtGradFuncObj;
  MoeTokenUnpermuteGradGradFunc MoeTokenUnpermuteGradGradFuncObj;
  InplaceCopyGradFunc InplaceCopyGradFuncObj;
  DotGradFunc DotGradFuncObj;
  ReplicationPad1DGradGradFunc ReplicationPad1DGradGradFuncObj;
  TransposeGradFunc TransposeGradFuncObj;
  SoftplusExtGradFunc SoftplusExtGradFuncObj;
  AbsGradFunc AbsGradFuncObj;
  LogicalAndGradFunc LogicalAndGradFuncObj;
  SplitTensorGradFunc SplitTensorGradFuncObj;
  GreaterEqualGradFunc GreaterEqualGradFuncObj;
  MultiScaleDeformableAttnGradFunc MultiScaleDeformableAttnGradFuncObj;
  GroupNormGradFunc GroupNormGradFuncObj;
  SplitGradFunc SplitGradFuncObj;
  SilentCheckV2GradFunc SilentCheckV2GradFuncObj;
  Im2ColExtGradFunc Im2ColExtGradFuncObj;
  IncreFlashAttentionGradFunc IncreFlashAttentionGradFuncObj;
  LogGradFunc LogGradFuncObj;
  NormalFloatTensorGradFunc NormalFloatTensorGradFuncObj;
  UpsampleNearest3DGradFunc UpsampleNearest3DGradFuncObj;
  InplaceFillTensorGradFunc InplaceFillTensorGradFuncObj;
  RoundGradFunc RoundGradFuncObj;
  TileGradFunc TileGradFuncObj;
  InplaceMulsGradFunc InplaceMulsGradFuncObj;
  ConcatGradFunc ConcatGradFuncObj;
  CustomExtGradFunc CustomExtGradFuncObj;
  ReduceMinGradFunc ReduceMinGradFuncObj;
  ReplicationPad2DGradFunc ReplicationPad2DGradFuncObj;
  InplaceSubExtGradFunc InplaceSubExtGradFuncObj;
  InplaceFillScalarGradFunc InplaceFillScalarGradFuncObj;
  CopyGradFunc CopyGradFuncObj;
  TensorScatterElementsGradFunc TensorScatterElementsGradFuncObj;
  DropoutDoMaskExtGradFunc DropoutDoMaskExtGradFuncObj;
  BitwiseOrTensorGradFunc BitwiseOrTensorGradFuncObj;
  SwigluGradFunc SwigluGradFuncObj;
  UpsampleNearest3DGradGradFunc UpsampleNearest3DGradGradFuncObj;
  ArgMinWithValueGradFunc ArgMinWithValueGradFuncObj;
  Conv2DExtGradFunc Conv2DExtGradFuncObj;
  DropoutGenMaskExtGradFunc DropoutGenMaskExtGradFuncObj;
  InplaceLogGradFunc InplaceLogGradFuncObj;
  Expm1GradFunc Expm1GradFuncObj;
  MulGradFunc MulGradFuncObj;
  L1LossExtGradFunc L1LossExtGradFuncObj;
  PromptFlashAttentionGradFunc PromptFlashAttentionGradFuncObj;
  MatrixInverseExtGradFunc MatrixInverseExtGradFuncObj;
  AddGradFunc AddGradFuncObj;
  HardtanhGradFunc HardtanhGradFuncObj;
  DropoutGradExtGradFunc DropoutGradExtGradFuncObj;
  LogicalNotGradFunc LogicalNotGradFuncObj;
  BatchMatMulExtGradFunc BatchMatMulExtGradFuncObj;
  BitwiseOrScalarGradFunc BitwiseOrScalarGradFuncObj;
  ReplicationPad2DGradGradFunc ReplicationPad2DGradGradFuncObj;
  SincGradFunc SincGradFuncObj;
  Conv1DPaddingGradFunc Conv1DPaddingGradFuncObj;
  GatherDGradFunc GatherDGradFuncObj;
  IdentityGradFunc IdentityGradFuncObj;
  HardtanhGradGradFunc HardtanhGradGradFuncObj;
  MaxDimGradFunc MaxDimGradFuncObj;
  SinGradFunc SinGradFuncObj;
  AdaptiveAvgPool3DExtGradFunc AdaptiveAvgPool3DExtGradFuncObj;
  QuantBatchMatmulGradFunc QuantBatchMatmulGradFuncObj;
  AddRmsNormQuantV2GradFunc AddRmsNormQuantV2GradFuncObj;
  DynamicQuantExtGradFunc DynamicQuantExtGradFuncObj;
  MoeComputeExpertTokensGradFunc MoeComputeExpertTokensGradFuncObj;
  GroupedMatmulGradFunc GroupedMatmulGradFuncObj;
  MatmulAllReduceAddRmsNormGradFunc MatmulAllReduceAddRmsNormGradFuncObj;
  KVCacheScatterUpdateGradFunc KVCacheScatterUpdateGradFuncObj;
  MoeInitRoutingGradFunc MoeInitRoutingGradFuncObj;
  MoeInitRoutingV2GradFunc MoeInitRoutingV2GradFuncObj;
  GroupedMatmulV2GradFunc GroupedMatmulV2GradFuncObj;
  MoeFinalizeRoutingGradFunc MoeFinalizeRoutingGradFuncObj;
  FusedInferAttentionScoreGradFunc FusedInferAttentionScoreGradFuncObj;
  QuantV2GradFunc QuantV2GradFuncObj;
  WeightQuantBatchMatmulGradFunc WeightQuantBatchMatmulGradFuncObj;
  GroupedMatmulV4GradFunc GroupedMatmulV4GradFuncObj;
  MoeGatingTopKSoftmaxGradFunc MoeGatingTopKSoftmaxGradFuncObj;
  PixelShuffleGradFunc PixelShuffleGradFuncObj;
};
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_
