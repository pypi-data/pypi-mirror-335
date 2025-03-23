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
  kUpsampleLinear1DGrad = 0,
  kInplaceFillDiagonal = 1,
  kRepeatInterleaveGrad = 2,
  kLogSigmoid = 3,
  kNormalFloatFloat = 4,
  kMaxPoolWithIndices = 5,
  kEqualExt = 6,
  kGridSampler2DGrad = 7,
  kNLLLoss2dGrad = 8,
  kReplicationPad2D = 9,
  kSelect = 10,
  kReplicationPad1D = 11,
  kInplaceScatterValue = 12,
  kOnesLikeExt = 13,
  kSlice = 14,
  kAddLayerNormGrad = 15,
  kFmodScalar = 16,
  kScatter = 17,
  kLayerNormGradExt = 18,
  kMSELossExt = 19,
  kLog2 = 20,
  kSpeedFusionAttention = 21,
  kAdaptiveAvgPool3DGradExt = 22,
  kSmoothL1LossGrad = 23,
  kScatterValue = 24,
  kStd = 25,
  kBatchNormGradExt = 26,
  kNotEqual = 27,
  kConvolutionStr = 28,
  kCosh = 29,
  kXlogy = 30,
  kConv3DExt = 31,
  kGroupNorm = 32,
  kAdaptiveMaxPool2D = 33,
  kReflectionPad3DGrad = 34,
  kDivMods = 35,
  kSqrt = 36,
  kClampScalar = 37,
  kConcat = 38,
  kReflectionPad3D = 39,
  kConvTranspose2D = 40,
  kFrac = 41,
  kCos = 42,
  kConv1DExt = 43,
  kTranspose = 44,
  kCummax = 45,
  kMatMulExt = 46,
  kInplaceDivs = 47,
  kNarrow = 48,
  kRandpermExt = 49,
  kPReLU = 50,
  kNormalTensorFloat = 51,
  kBCEWithLogitsLoss = 52,
  kLerp = 53,
  kIsNegInf = 54,
  kGatherDGradV2 = 55,
  kElu = 56,
  kGeluExt = 57,
  kConv2DExt = 58,
  kFloor = 59,
  kRmsNormGrad = 60,
  kRsqrt = 61,
  kAddScalar = 62,
  kSilentCheckV3 = 63,
  kBatchNormExt = 64,
  kMeanExt = 65,
  kBatchMatMul = 66,
  kAdaptiveAvgPool1D = 67,
  kEmbeddingDenseBackward = 68,
  kDense = 69,
  kFloorDiv = 70,
  kSquare = 71,
  kZerosLikeExt = 72,
  kInplaceNormal = 73,
  kAllFinite = 74,
  kCustomExt = 75,
  kDot = 76,
  kCast = 77,
  kInplaceClampTensor = 78,
  kSigmoidGrad = 79,
  kMishGradExt = 80,
  kErfinv = 81,
  kLogicalNot = 82,
  kBroadcastTo = 83,
  kLog1p = 84,
  kBinaryCrossEntropyWithLogitsBackward = 85,
  kExpandDims = 86,
  kMultiScaleDeformableAttn = 87,
  kIdentity = 88,
  kIsFinite = 89,
  kReLU = 90,
  kUpsampleNearest3DGrad = 91,
  kBernoulliExt = 92,
  kBinaryCrossEntropyGrad = 93,
  kMaskedSelect = 94,
  kLogSigmoidGrad = 95,
  kMoeTokenPermuteGrad = 96,
  kSearchSorted = 97,
  kBatchMatMulExt = 98,
  kInplaceThreshold = 99,
  kAsinExt = 100,
  kSmoothL1Loss = 101,
  kConvolution = 102,
  kSqueeze = 103,
  kSelectExt = 104,
  kSeLUExt = 105,
  kSplit = 106,
  kRandInt = 107,
  kMuls = 108,
  kConstantPadND = 109,
  kLogicalXor = 110,
  kMeshgrid = 111,
  kAddmv = 112,
  kAvgPool2DGrad = 113,
  kAdaptiveAvgPool2DGradExt = 114,
  kInplaceIndexAddExt = 115,
  kAddcdivExt = 116,
  kGeLU = 117,
  kBitwiseAndTensor = 118,
  kArgMinWithValue = 119,
  kAdaptiveMaxPool1D = 120,
  kPromptFlashAttention = 121,
  kFlashAttentionScore = 122,
  kRotaryPositionEmbeddingGrad = 123,
  kBitwiseXorScalar = 124,
  kInplaceUniform = 125,
  kNewOnes = 126,
  kRandLikeExt = 127,
  kUnstackExt = 128,
  kInplacePut = 129,
  kNLLLossGrad = 130,
  kHShrink = 131,
  kAddcmulExt = 132,
  kGcd = 133,
  kHardtanh = 134,
  kKLDivGrad = 135,
  kIndexFillTensor = 136,
  kLogicalOr = 137,
  kUpsampleNearest2DGrad = 138,
  kCol2ImExt = 139,
  kReshape = 140,
  kBitwiseOrScalar = 141,
  kSoftplusGradExt = 142,
  kSoftmax = 143,
  kFillScalar = 144,
  kGluGrad = 145,
  kBaddbmm = 146,
  kInplaceGroupedMatmulAdd = 147,
  kMul = 148,
  kMSELossGradExt = 149,
  kTransposeExt = 150,
  kUpsampleBilinear2D = 151,
  kRepeatInterleaveInt = 152,
  kCross = 153,
  kBitwiseXorTensor = 154,
  kSeluGrad = 155,
  kInplaceMaskedFillTensor = 156,
  kLog = 157,
  kThresholdGrad = 158,
  kUpsampleBicubic2D = 159,
  kLogAddExp2 = 160,
  kReduceAll = 161,
  kTan = 162,
  kViewAs = 163,
  kReciprocal = 164,
  kIsInf = 165,
  kBinaryCrossEntropy = 166,
  kUpsampleNearest1DGrad = 167,
  kGmmV2Backward = 168,
  kHSigmoidGrad = 169,
  kSubExt = 170,
  kUpsampleLinear1D = 171,
  kHShrinkGrad = 172,
  kFmodTensor = 173,
  kSplitTensor = 174,
  kCeil = 175,
  kUniqueDim = 176,
  kUpsampleBilinear2DGrad = 177,
  kGmmBackward = 178,
  kRound = 179,
  kInnerInplaceIndexPut = 180,
  kInplaceMuls = 181,
  kLinalgQr = 182,
  kInplaceFillScalar = 183,
  kIndexAddExt = 184,
  kInplaceZero = 185,
  kAvgPool3DGradExt = 186,
  kLogSoftmaxGrad = 187,
  kHSigmoid = 188,
  kMoeTokenUnpermute = 189,
  kIncreFlashAttention = 190,
  kMatrixInverseExt = 191,
  kRemainderTensorScalar = 192,
  kDiv = 193,
  kCol2ImGrad = 194,
  kBatchNormReduceGrad = 195,
  kView = 196,
  kRandExt = 197,
  kInplaceErfinv = 198,
  kNorm = 199,
  kMaximum = 200,
  kAdamW = 201,
  kUpsampleNearest1D = 202,
  kInplaceDivMod = 203,
  kInplaceRandom = 204,
  kContiguous = 205,
  kInplaceDiv = 206,
  kRmsNorm = 207,
  kOuter = 208,
  kRandIntLike = 209,
  kInnerIndex = 210,
  kCopy = 211,
  kInplaceAddExt = 212,
  kRotaryPositionEmbedding = 213,
  kDivs = 214,
  kInplaceScatterSrcReduce = 215,
  kNansum = 216,
  kDropoutExt = 217,
  kMatmulReduceScatter = 218,
  kReplicationPad1DGrad = 219,
  kFillTensor = 220,
  kUpsampleNearest2D = 221,
  kGridSampler3DGrad = 222,
  kFloorDivScalar = 223,
  kInplaceFillTensor = 224,
  kMinDim = 225,
  kMoeTokenPermute = 226,
  kLeakyReLUGradExt = 227,
  kClampTensor = 228,
  kNeg = 229,
  kGridSampler3D = 230,
  kSliceExt = 231,
  kAcosExt = 232,
  kAddbmm = 233,
  kMatMul = 234,
  kAdaptiveAvgPool3DExt = 235,
  kReflectionPad2D = 236,
  kLinalgVectorNorm = 237,
  kStdMean = 238,
  kSoftShrink = 239,
  kCountNonZero = 240,
  kSwigluGrad = 241,
  kGLU = 242,
  kInplaceScatterSrc = 243,
  kInplaceAddsExt = 244,
  kClone = 245,
  kReplicationPad3DGrad = 246,
  kTExt = 247,
  kUpsampleTrilinear3D = 248,
  kAddExt = 249,
  kEluExt = 250,
  kSign = 251,
  kUniqueConsecutive = 252,
  kSpeedFusionAttentionGrad = 253,
  kRemainderTensorTensor = 254,
  kMaxPoolGradWithIndices = 255,
  kGreaterEqual = 256,
  kArgSort = 257,
  kInnerNonZero = 258,
  kMultinomialExt = 259,
  kL1LossBackwardExt = 260,
  kLessEqual = 261,
  kLeakyReLUExt = 262,
  kConv1DPadding = 263,
  kAvgPool1D = 264,
  kGatherD = 265,
  kGeLUGrad = 266,
  kLogAddExp = 267,
  kExp2 = 268,
  kAllGatherMatmul = 269,
  kInplaceMul = 270,
  kLogSoftmaxExt = 271,
  kReplicationPad3D = 272,
  kInplaceFloorDivide = 273,
  kMaxDim = 274,
  kNonZeroExt = 275,
  kGreater = 276,
  kMin = 277,
  kReverseV2 = 278,
  kSiLU = 279,
  kConv2DPadding = 280,
  kInplaceAddmm = 281,
  kHistcExt = 282,
  kAdaptiveAvgPool2DExt = 283,
  kSplitWithSize = 284,
  kReplicationPad2DGrad = 285,
  kSoftMarginLossGrad = 286,
  kHSwishGrad = 287,
  kBatchNormElemt = 288,
  kNLLLoss = 289,
  kUnique2 = 290,
  kNormalFloatTensor = 291,
  kMm = 292,
  kInplaceClampScalar = 293,
  kLogSoftmax = 294,
  kAddmm = 295,
  kMultiScaleDeformableAttnGrad = 296,
  kNonZero = 297,
  kSub = 298,
  kOnes = 299,
  kBitwiseNot = 300,
  kInplaceStopGradient = 301,
  kTanh = 302,
  kCumsumExt = 303,
  kMoveTo = 304,
  kReduceMax = 305,
  kAdd = 306,
  kInplaceHardtanh = 307,
  kSwiglu = 308,
  kNewZeros = 309,
  kAddRmsNorm = 310,
  kSortExt = 311,
  kReduceMin = 312,
  kGreaterEqualScalar = 313,
  kVarMean = 314,
  kInplaceScatterAdd = 315,
  kCumminExt = 316,
  kGeluGradExt = 317,
  kIm2ColExt = 318,
  kChunk = 319,
  kPolar = 320,
  kMinimum = 321,
  kIsClose = 322,
  kSubScalar = 323,
  kEqual = 324,
  kInplaceSubExt = 325,
  kDiagExt = 326,
  kArgMinExt = 327,
  kInplaceElu = 328,
  kInplaceFloor = 329,
  kTraceExt = 330,
  kRemainderScalarTensor = 331,
  kInplaceReLU = 332,
  kUpsampleNearest3D = 333,
  kInplaceScatterValueReduce = 334,
  kReflectionPad1D = 335,
  kMaxUnpool2DExt = 336,
  kLinSpaceExt = 337,
  kRepeatInterleaveTensor = 338,
  kZeros = 339,
  kMv = 340,
  kGridSampler2D = 341,
  kLogicalAnd = 342,
  kConvolutionGrad = 343,
  kBincountExt = 344,
  kInplaceSubScalar = 345,
  kEluGradExt = 346,
  kReduceAny = 347,
  kFullLike = 348,
  kDropoutDoMaskExt = 349,
  kInplaceIndexPut = 350,
  kAsinhExt = 351,
  kMishExt = 352,
  kReflectionPad2DGrad = 353,
  kTypeAs = 354,
  kNLLLoss2d = 355,
  kTriangularSolve = 356,
  kMedianExt = 357,
  kMaskedFill = 358,
  kHardtanhGrad = 359,
  kAvgPool3DExt = 360,
  kRandn = 361,
  kDropoutGradExt = 362,
  kPReLUGrad = 363,
  kLerpScalar = 364,
  kReluGrad = 365,
  kArgMaxExt = 366,
  kSin = 367,
  kDivMod = 368,
  kFlashAttentionScoreGrad = 369,
  kStackExt = 370,
  kTanhGrad = 371,
  kTopkExt = 372,
  kBatchNormElemtGrad = 373,
  kIndex = 374,
  kPowScalarTensor = 375,
  kHSwish = 376,
  kProdExt = 377,
  kRandnLike = 378,
  kMaxPoolGradWithMask = 379,
  kMaxPoolWithMask = 380,
  kTile = 381,
  kUpsampleBicubic2DGrad = 382,
  kSelectV2 = 383,
  kScatterAddExt = 384,
  kSilentCheckV2 = 385,
  kTrilExt = 386,
  kBitwiseAndScalar = 387,
  kFFNExt = 388,
  kInplaceCopy = 389,
  kSinh = 390,
  kMoeTokenUnpermuteGrad = 391,
  kGenerator = 392,
  kDropoutGenMaskExt = 393,
  kExp = 394,
  kSigmoid = 395,
  kReflectionPad1DGrad = 396,
  kSumExt = 397,
  kConvolutionStrGrad = 398,
  kAtanExt = 399,
  kXLogYScalarOther = 400,
  kTrunc = 401,
  kInplaceLog = 402,
  kInplaceTanh = 403,
  kAvgPool2D = 404,
  kPowTensorScalar = 405,
  kBatchNormStats = 406,
  kVar = 407,
  kAsStrided = 408,
  kRoll = 409,
  kL1LossExt = 410,
  kLayerNormExt = 411,
  kSoftmaxBackward = 412,
  kExpandAs = 413,
  kIndexFillScalar = 414,
  kKthvalue = 415,
  kUniformExt = 416,
  kPow = 417,
  kBitwiseOrTensor = 418,
  kArange = 419,
  kNanToNum = 420,
  kSoftShrinkGrad = 421,
  kTake = 422,
  kAtan2Ext = 423,
  kGroupNormGrad = 424,
  kBatchNormGatherStatsWithCounts = 425,
  kNormalTensorTensor = 426,
  kMedianDim = 427,
  kArgMaxWithValue = 428,
  kTriu = 429,
  kErf = 430,
  kThreshold = 431,
  kErfc = 432,
  kAddLayerNormV2 = 433,
  kTensorScatterElements = 434,
  kAcoshExt = 435,
  kXLogYScalarSelf = 436,
  kInplaceExp = 437,
  kFlattenExt = 438,
  kNeScalar = 439,
  kExpm1 = 440,
  kInplaceFloorDivides = 441,
  kIndexSelect = 442,
  kMax = 443,
  kKLDiv = 444,
  kLogSumExp = 445,
  kInplaceMaskedFillScalar = 446,
  kEye = 447,
  kSiLUGrad = 448,
  kSoftMarginLoss = 449,
  kConv3DPadding = 450,
  kSoftplusExt = 451,
  kAtanh = 452,
  kLess = 453,
  kUpsampleTrilinear3DGrad = 454,
  kInplaceDivMods = 455,
  kEmbedding = 456,
  kAbs = 457,
  kRepeat = 458,
  kMaskedSelectGrad = 459,
  kOneHotExt = 460,
  kLog10 = 461,
  kSinc = 462,
  kMoeInitRouting = 463,
  kWeightQuantBatchMatmul = 464,
  kMoeInitRoutingV2 = 465,
  kGroupedMatmul = 466,
  kAddRmsNormQuantV2 = 467,
  kFusedInferAttentionScore = 468,
  kGroupedMatmulV2 = 469,
  kMoeGatingTopKSoftmax = 470,
  kMatmulAllReduceAddRmsNorm = 471,
  kKVCacheScatterUpdate = 472,
  kQuantV2 = 473,
  kMoeFinalizeRouting = 474,
  kMoeComputeExpertTokens = 475,
  kQuantBatchMatmul = 476,
  kGroupedMatmulV4 = 477,
  kDynamicQuantExt = 478,
  kPixelShuffle = 479,
};

using UpsampleLinear1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using InplaceFillDiagonalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using RepeatInterleaveGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using LogSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormalFloatFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxPoolWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using EqualExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GridSampler2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using NLLLoss2dGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReplicationPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReplicationPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using OnesLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SliceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using AddLayerNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FmodScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using LayerNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MSELossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using Log2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SpeedFusionAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using AdaptiveAvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SmoothL1LossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using StdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &)>;
using NotEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvolutionStrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using CoshGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using XlogyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using GroupNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using AdaptiveMaxPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ReflectionPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using DivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using ConcatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using ReflectionPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ConvTranspose2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using FracGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv1DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using TransposeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using CummaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceDivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using NarrowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RandpermExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using PReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormalTensorFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BCEWithLogitsLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using LerpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsNegInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GatherDGradV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using GeluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using Conv2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using FloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RmsNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RsqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SilentCheckV3GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using BatchNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using MeanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using BatchMatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AdaptiveAvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using EmbeddingDenseBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using DenseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using FloorDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SquareGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ZerosLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceNormalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AllFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using CustomExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using DotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CastGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using SigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MishGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogicalNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BroadcastToGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using Log1pGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BinaryCrossEntropyWithLogitsBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using ExpandDimsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MultiScaleDeformableAttnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IdentityGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using BernoulliExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BinaryCrossEntropyGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using MaskedSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MoeTokenPermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SearchSortedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchMatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using AsinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SmoothL1LossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ConvolutionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SqueezeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SelectExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using SeLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SplitGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RandIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ConstantPadNDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &)>;
using LogicalXorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MeshgridGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using AddmvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AvgPool2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AdaptiveAvgPool2DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceIndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using AddcdivExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using GeLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseAndTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ArgMinWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AdaptiveMaxPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using PromptFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using FlashAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RotaryPositionEmbeddingGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using BitwiseXorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceUniformGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NewOnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RandLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using UnstackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplacePutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using NLLLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using HShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using AddcmulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using GcdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using KLDivGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using IndexFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogicalOrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using Col2ImExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using ReshapeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using BitwiseOrScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SoftplusGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using FillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using GluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using BaddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using InplaceGroupedMatmulAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MSELossGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using TransposeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleBilinear2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using RepeatInterleaveIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using CrossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using BitwiseXorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SeluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceMaskedFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ThresholdGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using UpsampleBicubic2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using LogAddExp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReduceAllGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using TanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ViewAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReciprocalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BinaryCrossEntropyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using UpsampleNearest1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using GmmV2BackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using HSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using UpsampleLinear1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using HShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using FmodTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SplitTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using CeilGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UniqueDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleBilinear2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using GmmBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using RoundGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InnerInplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using InplaceMulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using LinalgQrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using IndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogSoftmaxGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using HSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MoeTokenUnpermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using IncreFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MatrixInverseExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RemainderTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using DivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Col2ImGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using BatchNormReduceGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using ViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using RandExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MaximumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AdamWGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using UpsampleNearest1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceDivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceRandomGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ContiguousGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using OuterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandIntLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InnerIndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using CopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using RotaryPositionEmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using DivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceScatterSrcReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using NansumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using DropoutExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MatmulReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using ReplicationPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using FillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using UpsampleNearest2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using GridSampler3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using FloorDivScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MinDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using MoeTokenPermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using LeakyReLUGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using ClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using NegGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GridSampler3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SliceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AcosExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AdaptiveAvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ReflectionPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using LinalgVectorNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using StdMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SoftShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using CountNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SwigluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using GLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceScatterSrcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceAddsExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using CloneGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReplicationPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using TExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleTrilinear3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using AddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using EluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using SignGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UniqueConsecutiveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SpeedFusionAttentionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using RemainderTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxPoolGradWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using GreaterEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ArgSortGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InnerNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MultinomialExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using L1LossBackwardExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using LessEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LeakyReLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using Conv1DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using AvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using GatherDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GeLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogAddExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Exp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AllGatherMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogSoftmaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReplicationPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceFloorDivideGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using NonZeroExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GreaterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReverseV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SiLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv2DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using InplaceAddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using HistcExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AdaptiveAvgPool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SplitWithSizeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using ReplicationPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SoftMarginLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using HSwishGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchNormElemtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using NLLLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using Unique2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using NormalFloatTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using LogSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using AddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MultiScaleDeformableAttnGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SubGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using OnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using BitwiseNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceStopGradientGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CumsumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MoveToGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::BoolImmPtr &)>;
using ReduceMaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using AddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceHardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SwigluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using NewZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using SortExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using ReduceMinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using GreaterEqualScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using VarMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceScatterAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CumminExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using GeluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using Im2ColExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using ChunkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using PolarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MinimumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsCloseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using SubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using EqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceSubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using DiagExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using ArgMinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using InplaceEluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceFloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TraceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RemainderScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplaceScatterValueReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using ReflectionPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MaxUnpool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using LinSpaceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RepeatInterleaveTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GridSampler2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using LogicalAndGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvolutionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using BincountExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using InplaceSubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using EluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using ReduceAnyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using FullLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using DropoutDoMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using AsinhExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MishExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReflectionPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using TypeAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NLLLoss2dGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using TriangularSolveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MedianExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaskedFillGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HardtanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RandnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using DropoutGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using PReLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LerpScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using ReluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ArgMaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using SinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using FlashAttentionScoreGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using StackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using TanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TopkExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchNormElemtGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using PowScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HSwishGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ProdExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RandnLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MaxPoolGradWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using MaxPoolWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using TileGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using UpsampleBicubic2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using SelectV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ScatterAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SilentCheckV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using TrilExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using BitwiseAndScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using FFNExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceCopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SinhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MoeTokenUnpermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using GeneratorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using DropoutGenMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using ExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReflectionPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ConvolutionStrGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using AtanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using XLogYScalarOtherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using TruncGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceLogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceTanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AvgPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using PowTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using BatchNormStatsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using VarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AsStridedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using RollGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using L1LossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using LayerNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using SoftmaxBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using ExpandAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IndexFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using KthvalueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using UniformExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using PowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseOrTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ArangeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NanToNumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &)>;
using SoftShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using TakeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Atan2ExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GroupNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchNormGatherStatsWithCountsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using NormalTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MedianDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ArgMaxWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using TriuGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using ErfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using ErfcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddLayerNormV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using TensorScatterElementsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AcoshExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using XLogYScalarSelfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FlattenExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using NeScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using Expm1GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceFloorDividesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using IndexSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using KLDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using LogSumExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using InplaceMaskedFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using EyeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using SiLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SoftMarginLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using Conv3DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SoftplusExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using AtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LessGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleTrilinear3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using InplaceDivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using EmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using AbsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RepeatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MaskedSelectGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using OneHotExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using Log10GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SincGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MoeInitRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using WeightQuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GroupedMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AddRmsNormQuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using FusedInferAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeGatingTopKSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using MatmulAllReduceAddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using KVCacheScatterUpdateGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using QuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeFinalizeRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using MoeComputeExpertTokensGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using QuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulV4GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using DynamicQuantExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using PixelShuffleGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;

struct OpsAutoGradRegisters {
  UpsampleLinear1DGradGradFunc UpsampleLinear1DGradGradFuncObj;
  InplaceFillDiagonalGradFunc InplaceFillDiagonalGradFuncObj;
  RepeatInterleaveGradGradFunc RepeatInterleaveGradGradFuncObj;
  LogSigmoidGradFunc LogSigmoidGradFuncObj;
  NormalFloatFloatGradFunc NormalFloatFloatGradFuncObj;
  MaxPoolWithIndicesGradFunc MaxPoolWithIndicesGradFuncObj;
  EqualExtGradFunc EqualExtGradFuncObj;
  GridSampler2DGradGradFunc GridSampler2DGradGradFuncObj;
  NLLLoss2dGradGradFunc NLLLoss2dGradGradFuncObj;
  ReplicationPad2DGradFunc ReplicationPad2DGradFuncObj;
  SelectGradFunc SelectGradFuncObj;
  ReplicationPad1DGradFunc ReplicationPad1DGradFuncObj;
  InplaceScatterValueGradFunc InplaceScatterValueGradFuncObj;
  OnesLikeExtGradFunc OnesLikeExtGradFuncObj;
  SliceGradFunc SliceGradFuncObj;
  AddLayerNormGradGradFunc AddLayerNormGradGradFuncObj;
  FmodScalarGradFunc FmodScalarGradFuncObj;
  ScatterGradFunc ScatterGradFuncObj;
  LayerNormGradExtGradFunc LayerNormGradExtGradFuncObj;
  MSELossExtGradFunc MSELossExtGradFuncObj;
  Log2GradFunc Log2GradFuncObj;
  SpeedFusionAttentionGradFunc SpeedFusionAttentionGradFuncObj;
  AdaptiveAvgPool3DGradExtGradFunc AdaptiveAvgPool3DGradExtGradFuncObj;
  SmoothL1LossGradGradFunc SmoothL1LossGradGradFuncObj;
  ScatterValueGradFunc ScatterValueGradFuncObj;
  StdGradFunc StdGradFuncObj;
  BatchNormGradExtGradFunc BatchNormGradExtGradFuncObj;
  NotEqualGradFunc NotEqualGradFuncObj;
  ConvolutionStrGradFunc ConvolutionStrGradFuncObj;
  CoshGradFunc CoshGradFuncObj;
  XlogyGradFunc XlogyGradFuncObj;
  Conv3DExtGradFunc Conv3DExtGradFuncObj;
  GroupNormGradFunc GroupNormGradFuncObj;
  AdaptiveMaxPool2DGradFunc AdaptiveMaxPool2DGradFuncObj;
  ReflectionPad3DGradGradFunc ReflectionPad3DGradGradFuncObj;
  DivModsGradFunc DivModsGradFuncObj;
  SqrtGradFunc SqrtGradFuncObj;
  ClampScalarGradFunc ClampScalarGradFuncObj;
  ConcatGradFunc ConcatGradFuncObj;
  ReflectionPad3DGradFunc ReflectionPad3DGradFuncObj;
  ConvTranspose2DGradFunc ConvTranspose2DGradFuncObj;
  FracGradFunc FracGradFuncObj;
  CosGradFunc CosGradFuncObj;
  Conv1DExtGradFunc Conv1DExtGradFuncObj;
  TransposeGradFunc TransposeGradFuncObj;
  CummaxGradFunc CummaxGradFuncObj;
  MatMulExtGradFunc MatMulExtGradFuncObj;
  InplaceDivsGradFunc InplaceDivsGradFuncObj;
  NarrowGradFunc NarrowGradFuncObj;
  RandpermExtGradFunc RandpermExtGradFuncObj;
  PReLUGradFunc PReLUGradFuncObj;
  NormalTensorFloatGradFunc NormalTensorFloatGradFuncObj;
  BCEWithLogitsLossGradFunc BCEWithLogitsLossGradFuncObj;
  LerpGradFunc LerpGradFuncObj;
  IsNegInfGradFunc IsNegInfGradFuncObj;
  GatherDGradV2GradFunc GatherDGradV2GradFuncObj;
  EluGradFunc EluGradFuncObj;
  GeluExtGradFunc GeluExtGradFuncObj;
  Conv2DExtGradFunc Conv2DExtGradFuncObj;
  FloorGradFunc FloorGradFuncObj;
  RmsNormGradGradFunc RmsNormGradGradFuncObj;
  RsqrtGradFunc RsqrtGradFuncObj;
  AddScalarGradFunc AddScalarGradFuncObj;
  SilentCheckV3GradFunc SilentCheckV3GradFuncObj;
  BatchNormExtGradFunc BatchNormExtGradFuncObj;
  MeanExtGradFunc MeanExtGradFuncObj;
  BatchMatMulGradFunc BatchMatMulGradFuncObj;
  AdaptiveAvgPool1DGradFunc AdaptiveAvgPool1DGradFuncObj;
  EmbeddingDenseBackwardGradFunc EmbeddingDenseBackwardGradFuncObj;
  DenseGradFunc DenseGradFuncObj;
  FloorDivGradFunc FloorDivGradFuncObj;
  SquareGradFunc SquareGradFuncObj;
  ZerosLikeExtGradFunc ZerosLikeExtGradFuncObj;
  InplaceNormalGradFunc InplaceNormalGradFuncObj;
  AllFiniteGradFunc AllFiniteGradFuncObj;
  CustomExtGradFunc CustomExtGradFuncObj;
  DotGradFunc DotGradFuncObj;
  CastGradFunc CastGradFuncObj;
  InplaceClampTensorGradFunc InplaceClampTensorGradFuncObj;
  SigmoidGradGradFunc SigmoidGradGradFuncObj;
  MishGradExtGradFunc MishGradExtGradFuncObj;
  ErfinvGradFunc ErfinvGradFuncObj;
  LogicalNotGradFunc LogicalNotGradFuncObj;
  BroadcastToGradFunc BroadcastToGradFuncObj;
  Log1pGradFunc Log1pGradFuncObj;
  BinaryCrossEntropyWithLogitsBackwardGradFunc BinaryCrossEntropyWithLogitsBackwardGradFuncObj;
  ExpandDimsGradFunc ExpandDimsGradFuncObj;
  MultiScaleDeformableAttnGradFunc MultiScaleDeformableAttnGradFuncObj;
  IdentityGradFunc IdentityGradFuncObj;
  IsFiniteGradFunc IsFiniteGradFuncObj;
  ReLUGradFunc ReLUGradFuncObj;
  UpsampleNearest3DGradGradFunc UpsampleNearest3DGradGradFuncObj;
  BernoulliExtGradFunc BernoulliExtGradFuncObj;
  BinaryCrossEntropyGradGradFunc BinaryCrossEntropyGradGradFuncObj;
  MaskedSelectGradFunc MaskedSelectGradFuncObj;
  LogSigmoidGradGradFunc LogSigmoidGradGradFuncObj;
  MoeTokenPermuteGradGradFunc MoeTokenPermuteGradGradFuncObj;
  SearchSortedGradFunc SearchSortedGradFuncObj;
  BatchMatMulExtGradFunc BatchMatMulExtGradFuncObj;
  InplaceThresholdGradFunc InplaceThresholdGradFuncObj;
  AsinExtGradFunc AsinExtGradFuncObj;
  SmoothL1LossGradFunc SmoothL1LossGradFuncObj;
  ConvolutionGradFunc ConvolutionGradFuncObj;
  SqueezeGradFunc SqueezeGradFuncObj;
  SelectExtGradFunc SelectExtGradFuncObj;
  SeLUExtGradFunc SeLUExtGradFuncObj;
  SplitGradFunc SplitGradFuncObj;
  RandIntGradFunc RandIntGradFuncObj;
  MulsGradFunc MulsGradFuncObj;
  ConstantPadNDGradFunc ConstantPadNDGradFuncObj;
  LogicalXorGradFunc LogicalXorGradFuncObj;
  MeshgridGradFunc MeshgridGradFuncObj;
  AddmvGradFunc AddmvGradFuncObj;
  AvgPool2DGradGradFunc AvgPool2DGradGradFuncObj;
  AdaptiveAvgPool2DGradExtGradFunc AdaptiveAvgPool2DGradExtGradFuncObj;
  InplaceIndexAddExtGradFunc InplaceIndexAddExtGradFuncObj;
  AddcdivExtGradFunc AddcdivExtGradFuncObj;
  GeLUGradFunc GeLUGradFuncObj;
  BitwiseAndTensorGradFunc BitwiseAndTensorGradFuncObj;
  ArgMinWithValueGradFunc ArgMinWithValueGradFuncObj;
  AdaptiveMaxPool1DGradFunc AdaptiveMaxPool1DGradFuncObj;
  PromptFlashAttentionGradFunc PromptFlashAttentionGradFuncObj;
  FlashAttentionScoreGradFunc FlashAttentionScoreGradFuncObj;
  RotaryPositionEmbeddingGradGradFunc RotaryPositionEmbeddingGradGradFuncObj;
  BitwiseXorScalarGradFunc BitwiseXorScalarGradFuncObj;
  InplaceUniformGradFunc InplaceUniformGradFuncObj;
  NewOnesGradFunc NewOnesGradFuncObj;
  RandLikeExtGradFunc RandLikeExtGradFuncObj;
  UnstackExtGradFunc UnstackExtGradFuncObj;
  InplacePutGradFunc InplacePutGradFuncObj;
  NLLLossGradGradFunc NLLLossGradGradFuncObj;
  HShrinkGradFunc HShrinkGradFuncObj;
  AddcmulExtGradFunc AddcmulExtGradFuncObj;
  GcdGradFunc GcdGradFuncObj;
  HardtanhGradFunc HardtanhGradFuncObj;
  KLDivGradGradFunc KLDivGradGradFuncObj;
  IndexFillTensorGradFunc IndexFillTensorGradFuncObj;
  LogicalOrGradFunc LogicalOrGradFuncObj;
  UpsampleNearest2DGradGradFunc UpsampleNearest2DGradGradFuncObj;
  Col2ImExtGradFunc Col2ImExtGradFuncObj;
  ReshapeGradFunc ReshapeGradFuncObj;
  BitwiseOrScalarGradFunc BitwiseOrScalarGradFuncObj;
  SoftplusGradExtGradFunc SoftplusGradExtGradFuncObj;
  SoftmaxGradFunc SoftmaxGradFuncObj;
  FillScalarGradFunc FillScalarGradFuncObj;
  GluGradGradFunc GluGradGradFuncObj;
  BaddbmmGradFunc BaddbmmGradFuncObj;
  InplaceGroupedMatmulAddGradFunc InplaceGroupedMatmulAddGradFuncObj;
  MulGradFunc MulGradFuncObj;
  MSELossGradExtGradFunc MSELossGradExtGradFuncObj;
  TransposeExtGradFunc TransposeExtGradFuncObj;
  UpsampleBilinear2DGradFunc UpsampleBilinear2DGradFuncObj;
  RepeatInterleaveIntGradFunc RepeatInterleaveIntGradFuncObj;
  CrossGradFunc CrossGradFuncObj;
  BitwiseXorTensorGradFunc BitwiseXorTensorGradFuncObj;
  SeluGradGradFunc SeluGradGradFuncObj;
  InplaceMaskedFillTensorGradFunc InplaceMaskedFillTensorGradFuncObj;
  LogGradFunc LogGradFuncObj;
  ThresholdGradGradFunc ThresholdGradGradFuncObj;
  UpsampleBicubic2DGradFunc UpsampleBicubic2DGradFuncObj;
  LogAddExp2GradFunc LogAddExp2GradFuncObj;
  ReduceAllGradFunc ReduceAllGradFuncObj;
  TanGradFunc TanGradFuncObj;
  ViewAsGradFunc ViewAsGradFuncObj;
  ReciprocalGradFunc ReciprocalGradFuncObj;
  IsInfGradFunc IsInfGradFuncObj;
  BinaryCrossEntropyGradFunc BinaryCrossEntropyGradFuncObj;
  UpsampleNearest1DGradGradFunc UpsampleNearest1DGradGradFuncObj;
  GmmV2BackwardGradFunc GmmV2BackwardGradFuncObj;
  HSigmoidGradGradFunc HSigmoidGradGradFuncObj;
  SubExtGradFunc SubExtGradFuncObj;
  UpsampleLinear1DGradFunc UpsampleLinear1DGradFuncObj;
  HShrinkGradGradFunc HShrinkGradGradFuncObj;
  FmodTensorGradFunc FmodTensorGradFuncObj;
  SplitTensorGradFunc SplitTensorGradFuncObj;
  CeilGradFunc CeilGradFuncObj;
  UniqueDimGradFunc UniqueDimGradFuncObj;
  UpsampleBilinear2DGradGradFunc UpsampleBilinear2DGradGradFuncObj;
  GmmBackwardGradFunc GmmBackwardGradFuncObj;
  RoundGradFunc RoundGradFuncObj;
  InnerInplaceIndexPutGradFunc InnerInplaceIndexPutGradFuncObj;
  InplaceMulsGradFunc InplaceMulsGradFuncObj;
  LinalgQrGradFunc LinalgQrGradFuncObj;
  InplaceFillScalarGradFunc InplaceFillScalarGradFuncObj;
  IndexAddExtGradFunc IndexAddExtGradFuncObj;
  InplaceZeroGradFunc InplaceZeroGradFuncObj;
  AvgPool3DGradExtGradFunc AvgPool3DGradExtGradFuncObj;
  LogSoftmaxGradGradFunc LogSoftmaxGradGradFuncObj;
  HSigmoidGradFunc HSigmoidGradFuncObj;
  MoeTokenUnpermuteGradFunc MoeTokenUnpermuteGradFuncObj;
  IncreFlashAttentionGradFunc IncreFlashAttentionGradFuncObj;
  MatrixInverseExtGradFunc MatrixInverseExtGradFuncObj;
  RemainderTensorScalarGradFunc RemainderTensorScalarGradFuncObj;
  DivGradFunc DivGradFuncObj;
  Col2ImGradGradFunc Col2ImGradGradFuncObj;
  BatchNormReduceGradGradFunc BatchNormReduceGradGradFuncObj;
  ViewGradFunc ViewGradFuncObj;
  RandExtGradFunc RandExtGradFuncObj;
  InplaceErfinvGradFunc InplaceErfinvGradFuncObj;
  NormGradFunc NormGradFuncObj;
  MaximumGradFunc MaximumGradFuncObj;
  AdamWGradFunc AdamWGradFuncObj;
  UpsampleNearest1DGradFunc UpsampleNearest1DGradFuncObj;
  InplaceDivModGradFunc InplaceDivModGradFuncObj;
  InplaceRandomGradFunc InplaceRandomGradFuncObj;
  ContiguousGradFunc ContiguousGradFuncObj;
  InplaceDivGradFunc InplaceDivGradFuncObj;
  RmsNormGradFunc RmsNormGradFuncObj;
  OuterGradFunc OuterGradFuncObj;
  RandIntLikeGradFunc RandIntLikeGradFuncObj;
  InnerIndexGradFunc InnerIndexGradFuncObj;
  CopyGradFunc CopyGradFuncObj;
  InplaceAddExtGradFunc InplaceAddExtGradFuncObj;
  RotaryPositionEmbeddingGradFunc RotaryPositionEmbeddingGradFuncObj;
  DivsGradFunc DivsGradFuncObj;
  InplaceScatterSrcReduceGradFunc InplaceScatterSrcReduceGradFuncObj;
  NansumGradFunc NansumGradFuncObj;
  DropoutExtGradFunc DropoutExtGradFuncObj;
  MatmulReduceScatterGradFunc MatmulReduceScatterGradFuncObj;
  ReplicationPad1DGradGradFunc ReplicationPad1DGradGradFuncObj;
  FillTensorGradFunc FillTensorGradFuncObj;
  UpsampleNearest2DGradFunc UpsampleNearest2DGradFuncObj;
  GridSampler3DGradGradFunc GridSampler3DGradGradFuncObj;
  FloorDivScalarGradFunc FloorDivScalarGradFuncObj;
  InplaceFillTensorGradFunc InplaceFillTensorGradFuncObj;
  MinDimGradFunc MinDimGradFuncObj;
  MoeTokenPermuteGradFunc MoeTokenPermuteGradFuncObj;
  LeakyReLUGradExtGradFunc LeakyReLUGradExtGradFuncObj;
  ClampTensorGradFunc ClampTensorGradFuncObj;
  NegGradFunc NegGradFuncObj;
  GridSampler3DGradFunc GridSampler3DGradFuncObj;
  SliceExtGradFunc SliceExtGradFuncObj;
  AcosExtGradFunc AcosExtGradFuncObj;
  AddbmmGradFunc AddbmmGradFuncObj;
  MatMulGradFunc MatMulGradFuncObj;
  AdaptiveAvgPool3DExtGradFunc AdaptiveAvgPool3DExtGradFuncObj;
  ReflectionPad2DGradFunc ReflectionPad2DGradFuncObj;
  LinalgVectorNormGradFunc LinalgVectorNormGradFuncObj;
  StdMeanGradFunc StdMeanGradFuncObj;
  SoftShrinkGradFunc SoftShrinkGradFuncObj;
  CountNonZeroGradFunc CountNonZeroGradFuncObj;
  SwigluGradGradFunc SwigluGradGradFuncObj;
  GLUGradFunc GLUGradFuncObj;
  InplaceScatterSrcGradFunc InplaceScatterSrcGradFuncObj;
  InplaceAddsExtGradFunc InplaceAddsExtGradFuncObj;
  CloneGradFunc CloneGradFuncObj;
  ReplicationPad3DGradGradFunc ReplicationPad3DGradGradFuncObj;
  TExtGradFunc TExtGradFuncObj;
  UpsampleTrilinear3DGradFunc UpsampleTrilinear3DGradFuncObj;
  AddExtGradFunc AddExtGradFuncObj;
  EluExtGradFunc EluExtGradFuncObj;
  SignGradFunc SignGradFuncObj;
  UniqueConsecutiveGradFunc UniqueConsecutiveGradFuncObj;
  SpeedFusionAttentionGradGradFunc SpeedFusionAttentionGradGradFuncObj;
  RemainderTensorTensorGradFunc RemainderTensorTensorGradFuncObj;
  MaxPoolGradWithIndicesGradFunc MaxPoolGradWithIndicesGradFuncObj;
  GreaterEqualGradFunc GreaterEqualGradFuncObj;
  ArgSortGradFunc ArgSortGradFuncObj;
  InnerNonZeroGradFunc InnerNonZeroGradFuncObj;
  MultinomialExtGradFunc MultinomialExtGradFuncObj;
  L1LossBackwardExtGradFunc L1LossBackwardExtGradFuncObj;
  LessEqualGradFunc LessEqualGradFuncObj;
  LeakyReLUExtGradFunc LeakyReLUExtGradFuncObj;
  Conv1DPaddingGradFunc Conv1DPaddingGradFuncObj;
  AvgPool1DGradFunc AvgPool1DGradFuncObj;
  GatherDGradFunc GatherDGradFuncObj;
  GeLUGradGradFunc GeLUGradGradFuncObj;
  LogAddExpGradFunc LogAddExpGradFuncObj;
  Exp2GradFunc Exp2GradFuncObj;
  AllGatherMatmulGradFunc AllGatherMatmulGradFuncObj;
  InplaceMulGradFunc InplaceMulGradFuncObj;
  LogSoftmaxExtGradFunc LogSoftmaxExtGradFuncObj;
  ReplicationPad3DGradFunc ReplicationPad3DGradFuncObj;
  InplaceFloorDivideGradFunc InplaceFloorDivideGradFuncObj;
  MaxDimGradFunc MaxDimGradFuncObj;
  NonZeroExtGradFunc NonZeroExtGradFuncObj;
  GreaterGradFunc GreaterGradFuncObj;
  MinGradFunc MinGradFuncObj;
  ReverseV2GradFunc ReverseV2GradFuncObj;
  SiLUGradFunc SiLUGradFuncObj;
  Conv2DPaddingGradFunc Conv2DPaddingGradFuncObj;
  InplaceAddmmGradFunc InplaceAddmmGradFuncObj;
  HistcExtGradFunc HistcExtGradFuncObj;
  AdaptiveAvgPool2DExtGradFunc AdaptiveAvgPool2DExtGradFuncObj;
  SplitWithSizeGradFunc SplitWithSizeGradFuncObj;
  ReplicationPad2DGradGradFunc ReplicationPad2DGradGradFuncObj;
  SoftMarginLossGradGradFunc SoftMarginLossGradGradFuncObj;
  HSwishGradGradFunc HSwishGradGradFuncObj;
  BatchNormElemtGradFunc BatchNormElemtGradFuncObj;
  NLLLossGradFunc NLLLossGradFuncObj;
  Unique2GradFunc Unique2GradFuncObj;
  NormalFloatTensorGradFunc NormalFloatTensorGradFuncObj;
  MmGradFunc MmGradFuncObj;
  InplaceClampScalarGradFunc InplaceClampScalarGradFuncObj;
  LogSoftmaxGradFunc LogSoftmaxGradFuncObj;
  AddmmGradFunc AddmmGradFuncObj;
  MultiScaleDeformableAttnGradGradFunc MultiScaleDeformableAttnGradGradFuncObj;
  NonZeroGradFunc NonZeroGradFuncObj;
  SubGradFunc SubGradFuncObj;
  OnesGradFunc OnesGradFuncObj;
  BitwiseNotGradFunc BitwiseNotGradFuncObj;
  InplaceStopGradientGradFunc InplaceStopGradientGradFuncObj;
  TanhGradFunc TanhGradFuncObj;
  CumsumExtGradFunc CumsumExtGradFuncObj;
  MoveToGradFunc MoveToGradFuncObj;
  ReduceMaxGradFunc ReduceMaxGradFuncObj;
  AddGradFunc AddGradFuncObj;
  InplaceHardtanhGradFunc InplaceHardtanhGradFuncObj;
  SwigluGradFunc SwigluGradFuncObj;
  NewZerosGradFunc NewZerosGradFuncObj;
  AddRmsNormGradFunc AddRmsNormGradFuncObj;
  SortExtGradFunc SortExtGradFuncObj;
  ReduceMinGradFunc ReduceMinGradFuncObj;
  GreaterEqualScalarGradFunc GreaterEqualScalarGradFuncObj;
  VarMeanGradFunc VarMeanGradFuncObj;
  InplaceScatterAddGradFunc InplaceScatterAddGradFuncObj;
  CumminExtGradFunc CumminExtGradFuncObj;
  GeluGradExtGradFunc GeluGradExtGradFuncObj;
  Im2ColExtGradFunc Im2ColExtGradFuncObj;
  ChunkGradFunc ChunkGradFuncObj;
  PolarGradFunc PolarGradFuncObj;
  MinimumGradFunc MinimumGradFuncObj;
  IsCloseGradFunc IsCloseGradFuncObj;
  SubScalarGradFunc SubScalarGradFuncObj;
  EqualGradFunc EqualGradFuncObj;
  InplaceSubExtGradFunc InplaceSubExtGradFuncObj;
  DiagExtGradFunc DiagExtGradFuncObj;
  ArgMinExtGradFunc ArgMinExtGradFuncObj;
  InplaceEluGradFunc InplaceEluGradFuncObj;
  InplaceFloorGradFunc InplaceFloorGradFuncObj;
  TraceExtGradFunc TraceExtGradFuncObj;
  RemainderScalarTensorGradFunc RemainderScalarTensorGradFuncObj;
  InplaceReLUGradFunc InplaceReLUGradFuncObj;
  UpsampleNearest3DGradFunc UpsampleNearest3DGradFuncObj;
  InplaceScatterValueReduceGradFunc InplaceScatterValueReduceGradFuncObj;
  ReflectionPad1DGradFunc ReflectionPad1DGradFuncObj;
  MaxUnpool2DExtGradFunc MaxUnpool2DExtGradFuncObj;
  LinSpaceExtGradFunc LinSpaceExtGradFuncObj;
  RepeatInterleaveTensorGradFunc RepeatInterleaveTensorGradFuncObj;
  ZerosGradFunc ZerosGradFuncObj;
  MvGradFunc MvGradFuncObj;
  GridSampler2DGradFunc GridSampler2DGradFuncObj;
  LogicalAndGradFunc LogicalAndGradFuncObj;
  ConvolutionGradGradFunc ConvolutionGradGradFuncObj;
  BincountExtGradFunc BincountExtGradFuncObj;
  InplaceSubScalarGradFunc InplaceSubScalarGradFuncObj;
  EluGradExtGradFunc EluGradExtGradFuncObj;
  ReduceAnyGradFunc ReduceAnyGradFuncObj;
  FullLikeGradFunc FullLikeGradFuncObj;
  DropoutDoMaskExtGradFunc DropoutDoMaskExtGradFuncObj;
  InplaceIndexPutGradFunc InplaceIndexPutGradFuncObj;
  AsinhExtGradFunc AsinhExtGradFuncObj;
  MishExtGradFunc MishExtGradFuncObj;
  ReflectionPad2DGradGradFunc ReflectionPad2DGradGradFuncObj;
  TypeAsGradFunc TypeAsGradFuncObj;
  NLLLoss2dGradFunc NLLLoss2dGradFuncObj;
  TriangularSolveGradFunc TriangularSolveGradFuncObj;
  MedianExtGradFunc MedianExtGradFuncObj;
  MaskedFillGradFunc MaskedFillGradFuncObj;
  HardtanhGradGradFunc HardtanhGradGradFuncObj;
  AvgPool3DExtGradFunc AvgPool3DExtGradFuncObj;
  RandnGradFunc RandnGradFuncObj;
  DropoutGradExtGradFunc DropoutGradExtGradFuncObj;
  PReLUGradGradFunc PReLUGradGradFuncObj;
  LerpScalarGradFunc LerpScalarGradFuncObj;
  ReluGradGradFunc ReluGradGradFuncObj;
  ArgMaxExtGradFunc ArgMaxExtGradFuncObj;
  SinGradFunc SinGradFuncObj;
  DivModGradFunc DivModGradFuncObj;
  FlashAttentionScoreGradGradFunc FlashAttentionScoreGradGradFuncObj;
  StackExtGradFunc StackExtGradFuncObj;
  TanhGradGradFunc TanhGradGradFuncObj;
  TopkExtGradFunc TopkExtGradFuncObj;
  BatchNormElemtGradGradFunc BatchNormElemtGradGradFuncObj;
  IndexGradFunc IndexGradFuncObj;
  PowScalarTensorGradFunc PowScalarTensorGradFuncObj;
  HSwishGradFunc HSwishGradFuncObj;
  ProdExtGradFunc ProdExtGradFuncObj;
  RandnLikeGradFunc RandnLikeGradFuncObj;
  MaxPoolGradWithMaskGradFunc MaxPoolGradWithMaskGradFuncObj;
  MaxPoolWithMaskGradFunc MaxPoolWithMaskGradFuncObj;
  TileGradFunc TileGradFuncObj;
  UpsampleBicubic2DGradGradFunc UpsampleBicubic2DGradGradFuncObj;
  SelectV2GradFunc SelectV2GradFuncObj;
  ScatterAddExtGradFunc ScatterAddExtGradFuncObj;
  SilentCheckV2GradFunc SilentCheckV2GradFuncObj;
  TrilExtGradFunc TrilExtGradFuncObj;
  BitwiseAndScalarGradFunc BitwiseAndScalarGradFuncObj;
  FFNExtGradFunc FFNExtGradFuncObj;
  InplaceCopyGradFunc InplaceCopyGradFuncObj;
  SinhGradFunc SinhGradFuncObj;
  MoeTokenUnpermuteGradGradFunc MoeTokenUnpermuteGradGradFuncObj;
  GeneratorGradFunc GeneratorGradFuncObj;
  DropoutGenMaskExtGradFunc DropoutGenMaskExtGradFuncObj;
  ExpGradFunc ExpGradFuncObj;
  SigmoidGradFunc SigmoidGradFuncObj;
  ReflectionPad1DGradGradFunc ReflectionPad1DGradGradFuncObj;
  SumExtGradFunc SumExtGradFuncObj;
  ConvolutionStrGradGradFunc ConvolutionStrGradGradFuncObj;
  AtanExtGradFunc AtanExtGradFuncObj;
  XLogYScalarOtherGradFunc XLogYScalarOtherGradFuncObj;
  TruncGradFunc TruncGradFuncObj;
  InplaceLogGradFunc InplaceLogGradFuncObj;
  InplaceTanhGradFunc InplaceTanhGradFuncObj;
  AvgPool2DGradFunc AvgPool2DGradFuncObj;
  PowTensorScalarGradFunc PowTensorScalarGradFuncObj;
  BatchNormStatsGradFunc BatchNormStatsGradFuncObj;
  VarGradFunc VarGradFuncObj;
  AsStridedGradFunc AsStridedGradFuncObj;
  RollGradFunc RollGradFuncObj;
  L1LossExtGradFunc L1LossExtGradFuncObj;
  LayerNormExtGradFunc LayerNormExtGradFuncObj;
  SoftmaxBackwardGradFunc SoftmaxBackwardGradFuncObj;
  ExpandAsGradFunc ExpandAsGradFuncObj;
  IndexFillScalarGradFunc IndexFillScalarGradFuncObj;
  KthvalueGradFunc KthvalueGradFuncObj;
  UniformExtGradFunc UniformExtGradFuncObj;
  PowGradFunc PowGradFuncObj;
  BitwiseOrTensorGradFunc BitwiseOrTensorGradFuncObj;
  ArangeGradFunc ArangeGradFuncObj;
  NanToNumGradFunc NanToNumGradFuncObj;
  SoftShrinkGradGradFunc SoftShrinkGradGradFuncObj;
  TakeGradFunc TakeGradFuncObj;
  Atan2ExtGradFunc Atan2ExtGradFuncObj;
  GroupNormGradGradFunc GroupNormGradGradFuncObj;
  BatchNormGatherStatsWithCountsGradFunc BatchNormGatherStatsWithCountsGradFuncObj;
  NormalTensorTensorGradFunc NormalTensorTensorGradFuncObj;
  MedianDimGradFunc MedianDimGradFuncObj;
  ArgMaxWithValueGradFunc ArgMaxWithValueGradFuncObj;
  TriuGradFunc TriuGradFuncObj;
  ErfGradFunc ErfGradFuncObj;
  ThresholdGradFunc ThresholdGradFuncObj;
  ErfcGradFunc ErfcGradFuncObj;
  AddLayerNormV2GradFunc AddLayerNormV2GradFuncObj;
  TensorScatterElementsGradFunc TensorScatterElementsGradFuncObj;
  AcoshExtGradFunc AcoshExtGradFuncObj;
  XLogYScalarSelfGradFunc XLogYScalarSelfGradFuncObj;
  InplaceExpGradFunc InplaceExpGradFuncObj;
  FlattenExtGradFunc FlattenExtGradFuncObj;
  NeScalarGradFunc NeScalarGradFuncObj;
  Expm1GradFunc Expm1GradFuncObj;
  InplaceFloorDividesGradFunc InplaceFloorDividesGradFuncObj;
  IndexSelectGradFunc IndexSelectGradFuncObj;
  MaxGradFunc MaxGradFuncObj;
  KLDivGradFunc KLDivGradFuncObj;
  LogSumExpGradFunc LogSumExpGradFuncObj;
  InplaceMaskedFillScalarGradFunc InplaceMaskedFillScalarGradFuncObj;
  EyeGradFunc EyeGradFuncObj;
  SiLUGradGradFunc SiLUGradGradFuncObj;
  SoftMarginLossGradFunc SoftMarginLossGradFuncObj;
  Conv3DPaddingGradFunc Conv3DPaddingGradFuncObj;
  SoftplusExtGradFunc SoftplusExtGradFuncObj;
  AtanhGradFunc AtanhGradFuncObj;
  LessGradFunc LessGradFuncObj;
  UpsampleTrilinear3DGradGradFunc UpsampleTrilinear3DGradGradFuncObj;
  InplaceDivModsGradFunc InplaceDivModsGradFuncObj;
  EmbeddingGradFunc EmbeddingGradFuncObj;
  AbsGradFunc AbsGradFuncObj;
  RepeatGradFunc RepeatGradFuncObj;
  MaskedSelectGradGradFunc MaskedSelectGradGradFuncObj;
  OneHotExtGradFunc OneHotExtGradFuncObj;
  Log10GradFunc Log10GradFuncObj;
  SincGradFunc SincGradFuncObj;
  MoeInitRoutingGradFunc MoeInitRoutingGradFuncObj;
  WeightQuantBatchMatmulGradFunc WeightQuantBatchMatmulGradFuncObj;
  MoeInitRoutingV2GradFunc MoeInitRoutingV2GradFuncObj;
  GroupedMatmulGradFunc GroupedMatmulGradFuncObj;
  AddRmsNormQuantV2GradFunc AddRmsNormQuantV2GradFuncObj;
  FusedInferAttentionScoreGradFunc FusedInferAttentionScoreGradFuncObj;
  GroupedMatmulV2GradFunc GroupedMatmulV2GradFuncObj;
  MoeGatingTopKSoftmaxGradFunc MoeGatingTopKSoftmaxGradFuncObj;
  MatmulAllReduceAddRmsNormGradFunc MatmulAllReduceAddRmsNormGradFuncObj;
  KVCacheScatterUpdateGradFunc KVCacheScatterUpdateGradFuncObj;
  QuantV2GradFunc QuantV2GradFuncObj;
  MoeFinalizeRoutingGradFunc MoeFinalizeRoutingGradFuncObj;
  MoeComputeExpertTokensGradFunc MoeComputeExpertTokensGradFuncObj;
  QuantBatchMatmulGradFunc QuantBatchMatmulGradFuncObj;
  GroupedMatmulV4GradFunc GroupedMatmulV4GradFuncObj;
  DynamicQuantExtGradFunc DynamicQuantExtGradFuncObj;
  PixelShuffleGradFunc PixelShuffleGradFuncObj;
};
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_
