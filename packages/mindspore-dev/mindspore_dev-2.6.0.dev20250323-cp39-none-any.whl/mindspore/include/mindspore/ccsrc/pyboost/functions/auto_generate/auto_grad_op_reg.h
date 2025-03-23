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
  kRemainderTensorScalar = 0,
  kStd = 1,
  kSelectExt = 2,
  kDivMod = 3,
  kScatterAddExt = 4,
  kInplaceMaskedFillScalar = 5,
  kSwigluGrad = 6,
  kPolar = 7,
  kCustomExt = 8,
  kFullLike = 9,
  kTypeAs = 10,
  kArange = 11,
  kMinDim = 12,
  kReplicationPad2D = 13,
  kSinc = 14,
  kGeluGradExt = 15,
  kOuter = 16,
  kGeluExt = 17,
  kHSigmoidGrad = 18,
  kIndexSelect = 19,
  kMm = 20,
  kConcat = 21,
  kLogicalXor = 22,
  kErfc = 23,
  kLessEqual = 24,
  kViewAs = 25,
  kNormalFloatTensor = 26,
  kKthvalue = 27,
  kArgMinWithValue = 28,
  kInplaceUniform = 29,
  kIsClose = 30,
  kMultiScaleDeformableAttn = 31,
  kThreshold = 32,
  kUnique2 = 33,
  kNotEqual = 34,
  kMaxPoolWithMask = 35,
  kNLLLossGrad = 36,
  kRepeatInterleaveTensor = 37,
  kArgMaxWithValue = 38,
  kGreater = 39,
  kInplaceDiv = 40,
  kAddLayerNormV2 = 41,
  kView = 42,
  kMaxPoolWithIndices = 43,
  kMSELossExt = 44,
  kArgMaxExt = 45,
  kFloorDiv = 46,
  kUpsampleTrilinear3D = 47,
  kNeg = 48,
  kClampTensor = 49,
  kBatchNormElemtGrad = 50,
  kMv = 51,
  kFlashAttentionScoreGrad = 52,
  kBinaryCrossEntropyGrad = 53,
  kMoeTokenPermuteGrad = 54,
  kInplaceStopGradient = 55,
  kExp2 = 56,
  kDivs = 57,
  kSliceExt = 58,
  kLogSoftmaxGrad = 59,
  kDropoutGenMaskExt = 60,
  kSortExt = 61,
  kBatchNormReduceGrad = 62,
  kIncreFlashAttention = 63,
  kVar = 64,
  kOnesLikeExt = 65,
  kFmodTensor = 66,
  kSlice = 67,
  kInplaceScatterValue = 68,
  kSmoothL1LossGrad = 69,
  kRoll = 70,
  kLogicalAnd = 71,
  kConv3DPadding = 72,
  kInplaceFloor = 73,
  kFrac = 74,
  kSplitWithSize = 75,
  kLog = 76,
  kMeshgrid = 77,
  kLinSpaceExt = 78,
  kGenerator = 79,
  kBitwiseNot = 80,
  kArgSort = 81,
  kAvgPool3DExt = 82,
  kLogAddExp = 83,
  kRandpermExt = 84,
  kBinaryCrossEntropyWithLogitsBackward = 85,
  kMultiScaleDeformableAttnGrad = 86,
  kSigmoid = 87,
  kMaxUnpool2DExt = 88,
  kAddcdivExt = 89,
  kAddcmulExt = 90,
  kStackExt = 91,
  kNonZeroExt = 92,
  kAsStrided = 93,
  kTranspose = 94,
  kReplicationPad1D = 95,
  kLayerNormExt = 96,
  kAdaptiveAvgPool2DGradExt = 97,
  kAvgPool1D = 98,
  kNonZero = 99,
  kLogSoftmaxExt = 100,
  kLess = 101,
  kEqual = 102,
  kConv2DExt = 103,
  kMaximum = 104,
  kNormalFloatFloat = 105,
  kRandIntLike = 106,
  kFloor = 107,
  kMoeTokenUnpermute = 108,
  kGatherD = 109,
  kConv1DExt = 110,
  kRandExt = 111,
  kRsqrt = 112,
  kTriangularSolve = 113,
  kAdd = 114,
  kInplaceLog = 115,
  kHSigmoid = 116,
  kUpsampleNearest1DGrad = 117,
  kLogSoftmax = 118,
  kProdExt = 119,
  kExpm1 = 120,
  kNanToNum = 121,
  kGridSampler3D = 122,
  kNormalTensorTensor = 123,
  kInplaceFloorDivides = 124,
  kLogicalOr = 125,
  kHSwish = 126,
  kRandLikeExt = 127,
  kTopkExt = 128,
  kMaskedSelectGrad = 129,
  kMishExt = 130,
  kReflectionPad2D = 131,
  kNewZeros = 132,
  kLogSumExp = 133,
  kCosh = 134,
  kIm2ColExt = 135,
  kOneHotExt = 136,
  kUpsampleLinear1D = 137,
  kSqueeze = 138,
  kPow = 139,
  kGridSampler2DGrad = 140,
  kConv3DExt = 141,
  kReshape = 142,
  kSeluGrad = 143,
  kCol2ImExt = 144,
  kMatMul = 145,
  kSelect = 146,
  kMinimum = 147,
  kMatMulExt = 148,
  kEmbedding = 149,
  kMin = 150,
  kReverseV2 = 151,
  kDivMods = 152,
  kXLogYScalarOther = 153,
  kConstantPadND = 154,
  kLayerNormGradExt = 155,
  kSumExt = 156,
  kUpsampleBicubic2DGrad = 157,
  kElu = 158,
  kGroupNorm = 159,
  kInplaceReLU = 160,
  kRemainderScalarTensor = 161,
  kSoftmaxBackward = 162,
  kFillScalar = 163,
  kSmoothL1Loss = 164,
  kAtan2Ext = 165,
  kInplaceThreshold = 166,
  kAbs = 167,
  kAtanh = 168,
  kLogSigmoidGrad = 169,
  kInplaceNormal = 170,
  kInplaceScatterValueReduce = 171,
  kEluGradExt = 172,
  kLerpScalar = 173,
  kDropoutDoMaskExt = 174,
  kMaskedSelect = 175,
  kIsInf = 176,
  kLeakyReLUExt = 177,
  kSilentCheckV2 = 178,
  kTan = 179,
  kInplaceFillScalar = 180,
  kExp = 181,
  kSplit = 182,
  kTraceExt = 183,
  kAdaptiveMaxPool2D = 184,
  kMatrixInverseExt = 185,
  kNormalTensorFloat = 186,
  kGridSampler2D = 187,
  kConv1DPadding = 188,
  kMul = 189,
  kDropoutExt = 190,
  kCross = 191,
  kAvgPool2DGrad = 192,
  kReflectionPad3DGrad = 193,
  kInplaceAddmm = 194,
  kMatmulReduceScatter = 195,
  kNeScalar = 196,
  kAllFinite = 197,
  kRotaryPositionEmbeddingGrad = 198,
  kRotaryPositionEmbedding = 199,
  kAdamW = 200,
  kInplaceTanh = 201,
  kHShrinkGrad = 202,
  kNLLLoss = 203,
  kMoeTokenPermute = 204,
  kExpandAs = 205,
  kTransposeExt = 206,
  kCummax = 207,
  kAddRmsNorm = 208,
  kSoftShrink = 209,
  kGridSampler3DGrad = 210,
  kLeakyReLUGradExt = 211,
  kReflectionPad2DGrad = 212,
  kIdentity = 213,
  kReplicationPad1DGrad = 214,
  kAddLayerNormGrad = 215,
  kTanhGrad = 216,
  kInplaceErfinv = 217,
  kAsinhExt = 218,
  kHardtanh = 219,
  kXLogYScalarSelf = 220,
  kScatter = 221,
  kTrilExt = 222,
  kDense = 223,
  kNLLLoss2dGrad = 224,
  kBernoulliExt = 225,
  kAllGatherMatmul = 226,
  kBatchMatMul = 227,
  kNansum = 228,
  kMoveTo = 229,
  kInplaceGroupedMatmulAdd = 230,
  kCos = 231,
  kBatchMatMulExt = 232,
  kBincountExt = 233,
  kReduceAny = 234,
  kExpandDims = 235,
  kInplaceFillTensor = 236,
  kUpsampleBicubic2D = 237,
  kRepeat = 238,
  kInplaceAddsExt = 239,
  kInplaceAddExt = 240,
  kGcd = 241,
  kUpsampleNearest2D = 242,
  kBatchNormStats = 243,
  kHardtanhGrad = 244,
  kEqualExt = 245,
  kUpsampleTrilinear3DGrad = 246,
  kConvolutionGrad = 247,
  kSin = 248,
  kCountNonZero = 249,
  kRmsNorm = 250,
  kConvTranspose2D = 251,
  kMSELossGradExt = 252,
  kHShrink = 253,
  kReplicationPad3DGrad = 254,
  kReLU = 255,
  kIndexAddExt = 256,
  kInplaceDivMod = 257,
  kUpsampleNearest1D = 258,
  kInplacePut = 259,
  kInplaceDivMods = 260,
  kMeanExt = 261,
  kIndex = 262,
  kHSwishGrad = 263,
  kNorm = 264,
  kOnes = 265,
  kL1LossBackwardExt = 266,
  kSoftplusExt = 267,
  kMuls = 268,
  kAcoshExt = 269,
  kMoeTokenUnpermuteGrad = 270,
  kThresholdGrad = 271,
  kPReLU = 272,
  kGeLU = 273,
  kReciprocal = 274,
  kLerp = 275,
  kGmmV2Backward = 276,
  kAddbmm = 277,
  kReduceAll = 278,
  kSilentCheckV3 = 279,
  kMaxPoolGradWithIndices = 280,
  kLogSigmoid = 281,
  kBatchNormGradExt = 282,
  kPromptFlashAttention = 283,
  kArgMinExt = 284,
  kUpsampleNearest2DGrad = 285,
  kBitwiseOrScalar = 286,
  kSquare = 287,
  kUpsampleBilinear2DGrad = 288,
  kPowScalarTensor = 289,
  kInplaceMuls = 290,
  kInplaceExp = 291,
  kPReLUGrad = 292,
  kInplaceRandom = 293,
  kCopy = 294,
  kReduceMax = 295,
  kBatchNormExt = 296,
  kGreaterEqual = 297,
  kBitwiseAndScalar = 298,
  kBatchNormElemt = 299,
  kLog10 = 300,
  kSplitTensor = 301,
  kSwiglu = 302,
  kMaskedFill = 303,
  kSoftmax = 304,
  kCast = 305,
  kSearchSorted = 306,
  kIsNegInf = 307,
  kReplicationPad3D = 308,
  kGroupNormGrad = 309,
  kMaxPoolGradWithMask = 310,
  kAdaptiveMaxPool1D = 311,
  kInplaceScatterAdd = 312,
  kSinh = 313,
  kFmodScalar = 314,
  kReflectionPad1DGrad = 315,
  kContiguous = 316,
  kRandn = 317,
  kReduceMin = 318,
  kInplaceIndexAddExt = 319,
  kGeLUGrad = 320,
  kInplaceSubExt = 321,
  kAddmv = 322,
  kUniqueDim = 323,
  kZerosLikeExt = 324,
  kLogAddExp2 = 325,
  kAdaptiveAvgPool3DExt = 326,
  kL1LossExt = 327,
  kEye = 328,
  kUpsampleBilinear2D = 329,
  kErf = 330,
  kSoftMarginLossGrad = 331,
  kFlashAttentionScore = 332,
  kInplaceClampTensor = 333,
  kFloorDivScalar = 334,
  kUnstackExt = 335,
  kXlogy = 336,
  kRmsNormGrad = 337,
  kAddScalar = 338,
  kNarrow = 339,
  kTake = 340,
  kBitwiseXorScalar = 341,
  kInplaceSubScalar = 342,
  kBroadcastTo = 343,
  kKLDivGrad = 344,
  kBitwiseXorTensor = 345,
  kSqrt = 346,
  kAddExt = 347,
  kReplicationPad2DGrad = 348,
  kInplaceZero = 349,
  kTriu = 350,
  kMultinomialExt = 351,
  kInnerIndex = 352,
  kInplaceClampScalar = 353,
  kUpsampleNearest3D = 354,
  kReflectionPad3D = 355,
  kBitwiseAndTensor = 356,
  kBatchNormGatherStatsWithCounts = 357,
  kRandInt = 358,
  kTExt = 359,
  kInplaceFloorDivide = 360,
  kZeros = 361,
  kReluGrad = 362,
  kRandnLike = 363,
  kInplaceDivs = 364,
  kSoftShrinkGrad = 365,
  kTanh = 366,
  kBaddbmm = 367,
  kGmmBackward = 368,
  kIndexFillScalar = 369,
  kDiv = 370,
  kSoftMarginLoss = 371,
  kRepeatInterleaveInt = 372,
  kUniqueConsecutive = 373,
  kSiLU = 374,
  kVarMean = 375,
  kErfinv = 376,
  kSigmoidGrad = 377,
  kMax = 378,
  kAdaptiveAvgPool1D = 379,
  kSubExt = 380,
  kDot = 381,
  kTile = 382,
  kLog2 = 383,
  kRepeatInterleaveGrad = 384,
  kCumsumExt = 385,
  kMedianExt = 386,
  kLog1p = 387,
  kHistcExt = 388,
  kMaxDim = 389,
  kGluGrad = 390,
  kSub = 391,
  kClone = 392,
  kInplaceMaskedFillTensor = 393,
  kMedianDim = 394,
  kUniformExt = 395,
  kSign = 396,
  kTensorScatterElements = 397,
  kTrunc = 398,
  kNewOnes = 399,
  kAvgPool2D = 400,
  kLinalgQr = 401,
  kIndexFillTensor = 402,
  kIsFinite = 403,
  kGLU = 404,
  kInplaceMul = 405,
  kDiagExt = 406,
  kSiLUGrad = 407,
  kFlattenExt = 408,
  kCol2ImGrad = 409,
  kInplaceCopy = 410,
  kLogicalNot = 411,
  kInnerInplaceIndexPut = 412,
  kKLDiv = 413,
  kAtanExt = 414,
  kStdMean = 415,
  kAdaptiveAvgPool2DExt = 416,
  kUpsampleNearest3DGrad = 417,
  kSpeedFusionAttention = 418,
  kConv2DPadding = 419,
  kClampScalar = 420,
  kRound = 421,
  kInplaceScatterSrcReduce = 422,
  kInplaceScatterSrc = 423,
  kMishGradExt = 424,
  kUpsampleLinear1DGrad = 425,
  kAcosExt = 426,
  kFFNExt = 427,
  kInplaceFillDiagonal = 428,
  kFillTensor = 429,
  kBinaryCrossEntropy = 430,
  kCeil = 431,
  kEluExt = 432,
  kSelectV2 = 433,
  kSeLUExt = 434,
  kEmbeddingDenseBackward = 435,
  kGatherDGradV2 = 436,
  kAsinExt = 437,
  kConvolutionStr = 438,
  kSoftplusGradExt = 439,
  kDropoutGradExt = 440,
  kInplaceIndexPut = 441,
  kInplaceHardtanh = 442,
  kSpeedFusionAttentionGrad = 443,
  kReflectionPad1D = 444,
  kChunk = 445,
  kBCEWithLogitsLoss = 446,
  kScatterValue = 447,
  kAvgPool3DGradExt = 448,
  kRemainderTensorTensor = 449,
  kLinalgVectorNorm = 450,
  kNLLLoss2d = 451,
  kAdaptiveAvgPool3DGradExt = 452,
  kInplaceElu = 453,
  kAddmm = 454,
  kInnerNonZero = 455,
  kConvolutionStrGrad = 456,
  kBitwiseOrTensor = 457,
  kCumminExt = 458,
  kPowTensorScalar = 459,
  kGreaterEqualScalar = 460,
  kSubScalar = 461,
  kConvolution = 462,
  kMoeInitRouting = 463,
  kGroupedMatmulV2 = 464,
  kDynamicQuantExt = 465,
  kMoeComputeExpertTokens = 466,
  kQuantV2 = 467,
  kQuantBatchMatmul = 468,
  kMoeGatingTopKSoftmax = 469,
  kFusedInferAttentionScore = 470,
  kMoeFinalizeRouting = 471,
  kGroupedMatmulV4 = 472,
  kKVCacheScatterUpdate = 473,
  kAddRmsNormQuantV2 = 474,
  kGroupedMatmul = 475,
  kMoeInitRoutingV2 = 476,
  kWeightQuantBatchMatmul = 477,
  kMatmulAllReduceAddRmsNorm = 478,
  kPixelShuffle = 479,
};

using RemainderTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using StdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using SelectExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using DivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ScatterAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceMaskedFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SwigluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using PolarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CustomExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using FullLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using TypeAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ArangeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MinDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ReplicationPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SincGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GeluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using OuterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GeluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using HSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IndexSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConcatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using LogicalXorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ErfcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LessEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ViewAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormalFloatTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using KthvalueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ArgMinWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceUniformGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsCloseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using MultiScaleDeformableAttnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using Unique2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using NotEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxPoolWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using NLLLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RepeatInterleaveTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ArgMaxWithValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GreaterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddLayerNormV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using ViewGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MaxPoolWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using MSELossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using ArgMaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using FloorDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleTrilinear3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using NegGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using BatchNormElemtGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FlashAttentionScoreGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using BinaryCrossEntropyGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using MoeTokenPermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceStopGradientGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Exp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SliceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using LogSoftmaxGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using DropoutGenMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using SortExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchNormReduceGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using IncreFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using VarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using OnesLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using FmodTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SliceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using InplaceScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SmoothL1LossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using RollGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using LogicalAndGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv3DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using InplaceFloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FracGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SplitWithSizeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using LogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MeshgridGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using LinSpaceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using GeneratorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using BitwiseNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ArgSortGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogAddExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandpermExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using BinaryCrossEntropyWithLogitsBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using MultiScaleDeformableAttnGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxUnpool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using AddcdivExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using AddcmulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using StackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using NonZeroExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AsStridedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using TransposeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ReplicationPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using LayerNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using AdaptiveAvgPool2DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using NonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogSoftmaxExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LessGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using MaximumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormalFloatFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandIntLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using FloorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MoeTokenUnpermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using GatherDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Conv1DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using RandExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RsqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TriangularSolveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using AddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceLogGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using LogSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using ProdExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using Expm1GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NanToNumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &)>;
using GridSampler3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using NormalTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceFloorDividesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using LogicalOrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HSwishGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using TopkExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MaskedSelectGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MishExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReflectionPad2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using NewZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogSumExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using CoshGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Im2ColExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using OneHotExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleLinear1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using SqueezeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using PowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GridSampler2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using Conv3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using ReshapeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SeluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Col2ImExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using MatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using SelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MinimumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::FP32ImmPtr> &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using MinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReverseV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using DivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using XLogYScalarOtherGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ConstantPadNDGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &)>;
using LayerNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using UpsampleBicubic2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using EluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using GroupNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using InplaceReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RemainderScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SoftmaxBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using FillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SmoothL1LossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using Atan2ExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceThresholdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using AbsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogSigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceNormalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceScatterValueReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using EluGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &)>;
using LerpScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using DropoutDoMaskExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using MaskedSelectGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LeakyReLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SilentCheckV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using TanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SplitGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using TraceExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AdaptiveMaxPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using MatrixInverseExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormalTensorFloatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GridSampler2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using Conv1DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using MulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DropoutExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CrossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using AvgPool2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReflectionPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceAddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MatmulReduceScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using NeScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using AllFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &)>;
using RotaryPositionEmbeddingGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using RotaryPositionEmbeddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using AdamWGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceTanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using NLLLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeTokenPermuteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using ExpandAsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TransposeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using CummaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using AddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using SoftShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using GridSampler3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &)>;
using LeakyReLUGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using ReflectionPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using IdentityGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReplicationPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using AddLayerNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AsinhExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using XLogYScalarSelfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ScatterGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using TrilExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using DenseGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using NLLLoss2dGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BernoulliExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AllGatherMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using BatchMatMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using NansumGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MoveToGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::StringImmPtr &, const mindspore::BoolImmPtr &)>;
using InplaceGroupedMatmulAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchMatMulExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BincountExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using ReduceAnyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using ExpandDimsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleBicubic2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using RepeatGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceAddsExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using InplaceAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using GcdGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleNearest2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using BatchNormStatsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using HardtanhGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using EqualExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleTrilinear3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using ConvolutionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using SinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CountNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using RmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using ConvTranspose2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using MSELossGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using HShrinkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using ReplicationPad3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceDivModGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using UpsampleNearest1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using InplacePutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using InplaceDivModsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MeanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using IndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using HSwishGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using OnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using L1LossBackwardExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using SoftplusExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using AcoshExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MoeTokenUnpermuteGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ThresholdGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using PReLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GeLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReciprocalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LerpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GmmV2BackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using AddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ReduceAllGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using SilentCheckV3GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MaxPoolGradWithIndicesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using LogSigmoidGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchNormGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::ValueTuplePtr &)>;
using PromptFlashAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using ArgMinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using UpsampleNearest2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using BitwiseOrScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SquareGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleBilinear2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using PowScalarTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceMulsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceExpGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using PReLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceRandomGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReduceMaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using BatchNormExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &)>;
using GreaterEqualGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseAndScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using BatchNormElemtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &)>;
using Log10GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SplitTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using SwigluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MaskedFillGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using CastGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using SearchSortedGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using IsNegInfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ReplicationPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using GroupNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MaxPoolGradWithMaskGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using AdaptiveMaxPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceScatterAddGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SinhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FmodScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ReflectionPad1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ContiguousGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandnGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReduceMinGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &)>;
using InplaceIndexAddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using GeLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceSubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using AddmvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using UniqueDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using ZerosLikeExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LogAddExp2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AdaptiveAvgPool3DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using L1LossExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using EyeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using UpsampleBilinear2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using ErfGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SoftMarginLossGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using FlashAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceClampTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using FloorDivScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using UnstackExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using XlogyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RmsNormGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using NarrowGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using TakeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BitwiseXorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using InplaceSubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using BroadcastToGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using KLDivGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using BitwiseXorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SqrtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AddExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using ReplicationPad2DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TriuGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using MultinomialExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InnerIndexGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using InplaceClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using UpsampleNearest3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ReflectionPad3DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using BitwiseAndTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BatchNormGatherStatsWithCountsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using RandIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using TExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceFloorDivideGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ZerosGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using ReluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RandnLikeGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using InplaceDivsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SoftShrinkGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using TanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using BaddbmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using GmmBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &)>;
using IndexFillScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using DivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SoftMarginLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using RepeatInterleaveIntGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const std::optional<mindspore::Int64ImmPtr> &)>;
using UniqueConsecutiveGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using SiLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using VarMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using ErfinvGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SigmoidGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AdaptiveAvgPool1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using SubExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using DotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TileGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using Log2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using RepeatInterleaveGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using CumsumExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using MedianExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using Log1pGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using HistcExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using MaxDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using GluGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using SubGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CloneGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceMaskedFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MedianDimGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using UniformExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SignGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using TensorScatterElementsGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using TruncGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using NewOnesGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using AvgPool2DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using LinalgQrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using IndexFillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using IsFiniteGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using GLUGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceMulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using DiagExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using SiLUGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FlattenExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using Col2ImGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &)>;
using InplaceCopyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LogicalNotGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InnerInplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using KLDivGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AtanExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using StdMeanGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using AdaptiveAvgPool2DExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using UpsampleNearest3DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using SpeedFusionAttentionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using Conv2DPaddingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using ClampScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ScalarPtr> &, const std::optional<mindspore::ScalarPtr> &)>;
using RoundGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceScatterSrcReduceGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceScatterSrcGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using MishGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using UpsampleLinear1DGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &)>;
using AcosExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using FFNExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using InplaceFillDiagonalGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::BoolImmPtr &)>;
using FillTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using BinaryCrossEntropyGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using CeilGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EluExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using SelectV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using SeLUExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using EmbeddingDenseBackwardGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::Int64ImmPtr> &, const mindspore::BoolImmPtr &)>;
using GatherDGradV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using AsinExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvolutionStrGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using SoftplusGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using DropoutGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using InplaceIndexPutGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &)>;
using InplaceHardtanhGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using SpeedFusionAttentionGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::FP32ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &)>;
using ReflectionPad1DGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &)>;
using ChunkGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using BCEWithLogitsLossGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using ScatterValueGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::Int64ImmPtr &)>;
using AvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using RemainderTensorTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using LinalgVectorNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::BoolImmPtr &, const std::optional<mindspore::Int64ImmPtr> &)>;
using NLLLoss2dGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AdaptiveAvgPool3DGradExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using InplaceEluGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using AddmmGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using InnerNonZeroGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using ConvolutionStrGradGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &, const mindspore::ValueTuplePtr &)>;
using BitwiseOrTensorGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &)>;
using CumminExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using PowTensorScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using GreaterEqualScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &)>;
using SubScalarGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ScalarPtr &, const mindspore::ScalarPtr &)>;
using ConvolutionGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const mindspore::BoolImmPtr &, const mindspore::ValueTuplePtr &, const mindspore::Int64ImmPtr &)>;
using MoeInitRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using GroupedMatmulV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using DynamicQuantExtGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using MoeComputeExpertTokensGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;
using QuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using QuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeGatingTopKSoftmaxGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &)>;
using FusedInferAttentionScoreGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::FP32ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using MoeFinalizeRoutingGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &)>;
using GroupedMatmulV4GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using KVCacheScatterUpdateGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using AddRmsNormQuantV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &)>;
using GroupedMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::ValueTuplePtr &, const mindspore::ValueTuplePtr &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::ValueTuplePtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &)>;
using MoeInitRoutingV2GradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::BoolImmPtr &)>;
using WeightQuantBatchMatmulGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const std::optional<mindspore::tensor::BaseTensorPtr> &, const mindspore::BoolImmPtr &, const mindspore::BoolImmPtr &, const mindspore::Int64ImmPtr &)>;
using MatmulAllReduceAddRmsNormGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::FP32ImmPtr &, const mindspore::StringImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &, const mindspore::Int64ImmPtr &)>;
using PixelShuffleGradFunc = std::function<void(const kernel::pyboost::OpPtr &, const mindspore::tensor::BaseTensorPtr &, const mindspore::Int64ImmPtr &)>;

struct OpsAutoGradRegisters {
  RemainderTensorScalarGradFunc RemainderTensorScalarGradFuncObj;
  StdGradFunc StdGradFuncObj;
  SelectExtGradFunc SelectExtGradFuncObj;
  DivModGradFunc DivModGradFuncObj;
  ScatterAddExtGradFunc ScatterAddExtGradFuncObj;
  InplaceMaskedFillScalarGradFunc InplaceMaskedFillScalarGradFuncObj;
  SwigluGradGradFunc SwigluGradGradFuncObj;
  PolarGradFunc PolarGradFuncObj;
  CustomExtGradFunc CustomExtGradFuncObj;
  FullLikeGradFunc FullLikeGradFuncObj;
  TypeAsGradFunc TypeAsGradFuncObj;
  ArangeGradFunc ArangeGradFuncObj;
  MinDimGradFunc MinDimGradFuncObj;
  ReplicationPad2DGradFunc ReplicationPad2DGradFuncObj;
  SincGradFunc SincGradFuncObj;
  GeluGradExtGradFunc GeluGradExtGradFuncObj;
  OuterGradFunc OuterGradFuncObj;
  GeluExtGradFunc GeluExtGradFuncObj;
  HSigmoidGradGradFunc HSigmoidGradGradFuncObj;
  IndexSelectGradFunc IndexSelectGradFuncObj;
  MmGradFunc MmGradFuncObj;
  ConcatGradFunc ConcatGradFuncObj;
  LogicalXorGradFunc LogicalXorGradFuncObj;
  ErfcGradFunc ErfcGradFuncObj;
  LessEqualGradFunc LessEqualGradFuncObj;
  ViewAsGradFunc ViewAsGradFuncObj;
  NormalFloatTensorGradFunc NormalFloatTensorGradFuncObj;
  KthvalueGradFunc KthvalueGradFuncObj;
  ArgMinWithValueGradFunc ArgMinWithValueGradFuncObj;
  InplaceUniformGradFunc InplaceUniformGradFuncObj;
  IsCloseGradFunc IsCloseGradFuncObj;
  MultiScaleDeformableAttnGradFunc MultiScaleDeformableAttnGradFuncObj;
  ThresholdGradFunc ThresholdGradFuncObj;
  Unique2GradFunc Unique2GradFuncObj;
  NotEqualGradFunc NotEqualGradFuncObj;
  MaxPoolWithMaskGradFunc MaxPoolWithMaskGradFuncObj;
  NLLLossGradGradFunc NLLLossGradGradFuncObj;
  RepeatInterleaveTensorGradFunc RepeatInterleaveTensorGradFuncObj;
  ArgMaxWithValueGradFunc ArgMaxWithValueGradFuncObj;
  GreaterGradFunc GreaterGradFuncObj;
  InplaceDivGradFunc InplaceDivGradFuncObj;
  AddLayerNormV2GradFunc AddLayerNormV2GradFuncObj;
  ViewGradFunc ViewGradFuncObj;
  MaxPoolWithIndicesGradFunc MaxPoolWithIndicesGradFuncObj;
  MSELossExtGradFunc MSELossExtGradFuncObj;
  ArgMaxExtGradFunc ArgMaxExtGradFuncObj;
  FloorDivGradFunc FloorDivGradFuncObj;
  UpsampleTrilinear3DGradFunc UpsampleTrilinear3DGradFuncObj;
  NegGradFunc NegGradFuncObj;
  ClampTensorGradFunc ClampTensorGradFuncObj;
  BatchNormElemtGradGradFunc BatchNormElemtGradGradFuncObj;
  MvGradFunc MvGradFuncObj;
  FlashAttentionScoreGradGradFunc FlashAttentionScoreGradGradFuncObj;
  BinaryCrossEntropyGradGradFunc BinaryCrossEntropyGradGradFuncObj;
  MoeTokenPermuteGradGradFunc MoeTokenPermuteGradGradFuncObj;
  InplaceStopGradientGradFunc InplaceStopGradientGradFuncObj;
  Exp2GradFunc Exp2GradFuncObj;
  DivsGradFunc DivsGradFuncObj;
  SliceExtGradFunc SliceExtGradFuncObj;
  LogSoftmaxGradGradFunc LogSoftmaxGradGradFuncObj;
  DropoutGenMaskExtGradFunc DropoutGenMaskExtGradFuncObj;
  SortExtGradFunc SortExtGradFuncObj;
  BatchNormReduceGradGradFunc BatchNormReduceGradGradFuncObj;
  IncreFlashAttentionGradFunc IncreFlashAttentionGradFuncObj;
  VarGradFunc VarGradFuncObj;
  OnesLikeExtGradFunc OnesLikeExtGradFuncObj;
  FmodTensorGradFunc FmodTensorGradFuncObj;
  SliceGradFunc SliceGradFuncObj;
  InplaceScatterValueGradFunc InplaceScatterValueGradFuncObj;
  SmoothL1LossGradGradFunc SmoothL1LossGradGradFuncObj;
  RollGradFunc RollGradFuncObj;
  LogicalAndGradFunc LogicalAndGradFuncObj;
  Conv3DPaddingGradFunc Conv3DPaddingGradFuncObj;
  InplaceFloorGradFunc InplaceFloorGradFuncObj;
  FracGradFunc FracGradFuncObj;
  SplitWithSizeGradFunc SplitWithSizeGradFuncObj;
  LogGradFunc LogGradFuncObj;
  MeshgridGradFunc MeshgridGradFuncObj;
  LinSpaceExtGradFunc LinSpaceExtGradFuncObj;
  GeneratorGradFunc GeneratorGradFuncObj;
  BitwiseNotGradFunc BitwiseNotGradFuncObj;
  ArgSortGradFunc ArgSortGradFuncObj;
  AvgPool3DExtGradFunc AvgPool3DExtGradFuncObj;
  LogAddExpGradFunc LogAddExpGradFuncObj;
  RandpermExtGradFunc RandpermExtGradFuncObj;
  BinaryCrossEntropyWithLogitsBackwardGradFunc BinaryCrossEntropyWithLogitsBackwardGradFuncObj;
  MultiScaleDeformableAttnGradGradFunc MultiScaleDeformableAttnGradGradFuncObj;
  SigmoidGradFunc SigmoidGradFuncObj;
  MaxUnpool2DExtGradFunc MaxUnpool2DExtGradFuncObj;
  AddcdivExtGradFunc AddcdivExtGradFuncObj;
  AddcmulExtGradFunc AddcmulExtGradFuncObj;
  StackExtGradFunc StackExtGradFuncObj;
  NonZeroExtGradFunc NonZeroExtGradFuncObj;
  AsStridedGradFunc AsStridedGradFuncObj;
  TransposeGradFunc TransposeGradFuncObj;
  ReplicationPad1DGradFunc ReplicationPad1DGradFuncObj;
  LayerNormExtGradFunc LayerNormExtGradFuncObj;
  AdaptiveAvgPool2DGradExtGradFunc AdaptiveAvgPool2DGradExtGradFuncObj;
  AvgPool1DGradFunc AvgPool1DGradFuncObj;
  NonZeroGradFunc NonZeroGradFuncObj;
  LogSoftmaxExtGradFunc LogSoftmaxExtGradFuncObj;
  LessGradFunc LessGradFuncObj;
  EqualGradFunc EqualGradFuncObj;
  Conv2DExtGradFunc Conv2DExtGradFuncObj;
  MaximumGradFunc MaximumGradFuncObj;
  NormalFloatFloatGradFunc NormalFloatFloatGradFuncObj;
  RandIntLikeGradFunc RandIntLikeGradFuncObj;
  FloorGradFunc FloorGradFuncObj;
  MoeTokenUnpermuteGradFunc MoeTokenUnpermuteGradFuncObj;
  GatherDGradFunc GatherDGradFuncObj;
  Conv1DExtGradFunc Conv1DExtGradFuncObj;
  RandExtGradFunc RandExtGradFuncObj;
  RsqrtGradFunc RsqrtGradFuncObj;
  TriangularSolveGradFunc TriangularSolveGradFuncObj;
  AddGradFunc AddGradFuncObj;
  InplaceLogGradFunc InplaceLogGradFuncObj;
  HSigmoidGradFunc HSigmoidGradFuncObj;
  UpsampleNearest1DGradGradFunc UpsampleNearest1DGradGradFuncObj;
  LogSoftmaxGradFunc LogSoftmaxGradFuncObj;
  ProdExtGradFunc ProdExtGradFuncObj;
  Expm1GradFunc Expm1GradFuncObj;
  NanToNumGradFunc NanToNumGradFuncObj;
  GridSampler3DGradFunc GridSampler3DGradFuncObj;
  NormalTensorTensorGradFunc NormalTensorTensorGradFuncObj;
  InplaceFloorDividesGradFunc InplaceFloorDividesGradFuncObj;
  LogicalOrGradFunc LogicalOrGradFuncObj;
  HSwishGradFunc HSwishGradFuncObj;
  RandLikeExtGradFunc RandLikeExtGradFuncObj;
  TopkExtGradFunc TopkExtGradFuncObj;
  MaskedSelectGradGradFunc MaskedSelectGradGradFuncObj;
  MishExtGradFunc MishExtGradFuncObj;
  ReflectionPad2DGradFunc ReflectionPad2DGradFuncObj;
  NewZerosGradFunc NewZerosGradFuncObj;
  LogSumExpGradFunc LogSumExpGradFuncObj;
  CoshGradFunc CoshGradFuncObj;
  Im2ColExtGradFunc Im2ColExtGradFuncObj;
  OneHotExtGradFunc OneHotExtGradFuncObj;
  UpsampleLinear1DGradFunc UpsampleLinear1DGradFuncObj;
  SqueezeGradFunc SqueezeGradFuncObj;
  PowGradFunc PowGradFuncObj;
  GridSampler2DGradGradFunc GridSampler2DGradGradFuncObj;
  Conv3DExtGradFunc Conv3DExtGradFuncObj;
  ReshapeGradFunc ReshapeGradFuncObj;
  SeluGradGradFunc SeluGradGradFuncObj;
  Col2ImExtGradFunc Col2ImExtGradFuncObj;
  MatMulGradFunc MatMulGradFuncObj;
  SelectGradFunc SelectGradFuncObj;
  MinimumGradFunc MinimumGradFuncObj;
  MatMulExtGradFunc MatMulExtGradFuncObj;
  EmbeddingGradFunc EmbeddingGradFuncObj;
  MinGradFunc MinGradFuncObj;
  ReverseV2GradFunc ReverseV2GradFuncObj;
  DivModsGradFunc DivModsGradFuncObj;
  XLogYScalarOtherGradFunc XLogYScalarOtherGradFuncObj;
  ConstantPadNDGradFunc ConstantPadNDGradFuncObj;
  LayerNormGradExtGradFunc LayerNormGradExtGradFuncObj;
  SumExtGradFunc SumExtGradFuncObj;
  UpsampleBicubic2DGradGradFunc UpsampleBicubic2DGradGradFuncObj;
  EluGradFunc EluGradFuncObj;
  GroupNormGradFunc GroupNormGradFuncObj;
  InplaceReLUGradFunc InplaceReLUGradFuncObj;
  RemainderScalarTensorGradFunc RemainderScalarTensorGradFuncObj;
  SoftmaxBackwardGradFunc SoftmaxBackwardGradFuncObj;
  FillScalarGradFunc FillScalarGradFuncObj;
  SmoothL1LossGradFunc SmoothL1LossGradFuncObj;
  Atan2ExtGradFunc Atan2ExtGradFuncObj;
  InplaceThresholdGradFunc InplaceThresholdGradFuncObj;
  AbsGradFunc AbsGradFuncObj;
  AtanhGradFunc AtanhGradFuncObj;
  LogSigmoidGradGradFunc LogSigmoidGradGradFuncObj;
  InplaceNormalGradFunc InplaceNormalGradFuncObj;
  InplaceScatterValueReduceGradFunc InplaceScatterValueReduceGradFuncObj;
  EluGradExtGradFunc EluGradExtGradFuncObj;
  LerpScalarGradFunc LerpScalarGradFuncObj;
  DropoutDoMaskExtGradFunc DropoutDoMaskExtGradFuncObj;
  MaskedSelectGradFunc MaskedSelectGradFuncObj;
  IsInfGradFunc IsInfGradFuncObj;
  LeakyReLUExtGradFunc LeakyReLUExtGradFuncObj;
  SilentCheckV2GradFunc SilentCheckV2GradFuncObj;
  TanGradFunc TanGradFuncObj;
  InplaceFillScalarGradFunc InplaceFillScalarGradFuncObj;
  ExpGradFunc ExpGradFuncObj;
  SplitGradFunc SplitGradFuncObj;
  TraceExtGradFunc TraceExtGradFuncObj;
  AdaptiveMaxPool2DGradFunc AdaptiveMaxPool2DGradFuncObj;
  MatrixInverseExtGradFunc MatrixInverseExtGradFuncObj;
  NormalTensorFloatGradFunc NormalTensorFloatGradFuncObj;
  GridSampler2DGradFunc GridSampler2DGradFuncObj;
  Conv1DPaddingGradFunc Conv1DPaddingGradFuncObj;
  MulGradFunc MulGradFuncObj;
  DropoutExtGradFunc DropoutExtGradFuncObj;
  CrossGradFunc CrossGradFuncObj;
  AvgPool2DGradGradFunc AvgPool2DGradGradFuncObj;
  ReflectionPad3DGradGradFunc ReflectionPad3DGradGradFuncObj;
  InplaceAddmmGradFunc InplaceAddmmGradFuncObj;
  MatmulReduceScatterGradFunc MatmulReduceScatterGradFuncObj;
  NeScalarGradFunc NeScalarGradFuncObj;
  AllFiniteGradFunc AllFiniteGradFuncObj;
  RotaryPositionEmbeddingGradGradFunc RotaryPositionEmbeddingGradGradFuncObj;
  RotaryPositionEmbeddingGradFunc RotaryPositionEmbeddingGradFuncObj;
  AdamWGradFunc AdamWGradFuncObj;
  InplaceTanhGradFunc InplaceTanhGradFuncObj;
  HShrinkGradGradFunc HShrinkGradGradFuncObj;
  NLLLossGradFunc NLLLossGradFuncObj;
  MoeTokenPermuteGradFunc MoeTokenPermuteGradFuncObj;
  ExpandAsGradFunc ExpandAsGradFuncObj;
  TransposeExtGradFunc TransposeExtGradFuncObj;
  CummaxGradFunc CummaxGradFuncObj;
  AddRmsNormGradFunc AddRmsNormGradFuncObj;
  SoftShrinkGradFunc SoftShrinkGradFuncObj;
  GridSampler3DGradGradFunc GridSampler3DGradGradFuncObj;
  LeakyReLUGradExtGradFunc LeakyReLUGradExtGradFuncObj;
  ReflectionPad2DGradGradFunc ReflectionPad2DGradGradFuncObj;
  IdentityGradFunc IdentityGradFuncObj;
  ReplicationPad1DGradGradFunc ReplicationPad1DGradGradFuncObj;
  AddLayerNormGradGradFunc AddLayerNormGradGradFuncObj;
  TanhGradGradFunc TanhGradGradFuncObj;
  InplaceErfinvGradFunc InplaceErfinvGradFuncObj;
  AsinhExtGradFunc AsinhExtGradFuncObj;
  HardtanhGradFunc HardtanhGradFuncObj;
  XLogYScalarSelfGradFunc XLogYScalarSelfGradFuncObj;
  ScatterGradFunc ScatterGradFuncObj;
  TrilExtGradFunc TrilExtGradFuncObj;
  DenseGradFunc DenseGradFuncObj;
  NLLLoss2dGradGradFunc NLLLoss2dGradGradFuncObj;
  BernoulliExtGradFunc BernoulliExtGradFuncObj;
  AllGatherMatmulGradFunc AllGatherMatmulGradFuncObj;
  BatchMatMulGradFunc BatchMatMulGradFuncObj;
  NansumGradFunc NansumGradFuncObj;
  MoveToGradFunc MoveToGradFuncObj;
  InplaceGroupedMatmulAddGradFunc InplaceGroupedMatmulAddGradFuncObj;
  CosGradFunc CosGradFuncObj;
  BatchMatMulExtGradFunc BatchMatMulExtGradFuncObj;
  BincountExtGradFunc BincountExtGradFuncObj;
  ReduceAnyGradFunc ReduceAnyGradFuncObj;
  ExpandDimsGradFunc ExpandDimsGradFuncObj;
  InplaceFillTensorGradFunc InplaceFillTensorGradFuncObj;
  UpsampleBicubic2DGradFunc UpsampleBicubic2DGradFuncObj;
  RepeatGradFunc RepeatGradFuncObj;
  InplaceAddsExtGradFunc InplaceAddsExtGradFuncObj;
  InplaceAddExtGradFunc InplaceAddExtGradFuncObj;
  GcdGradFunc GcdGradFuncObj;
  UpsampleNearest2DGradFunc UpsampleNearest2DGradFuncObj;
  BatchNormStatsGradFunc BatchNormStatsGradFuncObj;
  HardtanhGradGradFunc HardtanhGradGradFuncObj;
  EqualExtGradFunc EqualExtGradFuncObj;
  UpsampleTrilinear3DGradGradFunc UpsampleTrilinear3DGradGradFuncObj;
  ConvolutionGradGradFunc ConvolutionGradGradFuncObj;
  SinGradFunc SinGradFuncObj;
  CountNonZeroGradFunc CountNonZeroGradFuncObj;
  RmsNormGradFunc RmsNormGradFuncObj;
  ConvTranspose2DGradFunc ConvTranspose2DGradFuncObj;
  MSELossGradExtGradFunc MSELossGradExtGradFuncObj;
  HShrinkGradFunc HShrinkGradFuncObj;
  ReplicationPad3DGradGradFunc ReplicationPad3DGradGradFuncObj;
  ReLUGradFunc ReLUGradFuncObj;
  IndexAddExtGradFunc IndexAddExtGradFuncObj;
  InplaceDivModGradFunc InplaceDivModGradFuncObj;
  UpsampleNearest1DGradFunc UpsampleNearest1DGradFuncObj;
  InplacePutGradFunc InplacePutGradFuncObj;
  InplaceDivModsGradFunc InplaceDivModsGradFuncObj;
  MeanExtGradFunc MeanExtGradFuncObj;
  IndexGradFunc IndexGradFuncObj;
  HSwishGradGradFunc HSwishGradGradFuncObj;
  NormGradFunc NormGradFuncObj;
  OnesGradFunc OnesGradFuncObj;
  L1LossBackwardExtGradFunc L1LossBackwardExtGradFuncObj;
  SoftplusExtGradFunc SoftplusExtGradFuncObj;
  MulsGradFunc MulsGradFuncObj;
  AcoshExtGradFunc AcoshExtGradFuncObj;
  MoeTokenUnpermuteGradGradFunc MoeTokenUnpermuteGradGradFuncObj;
  ThresholdGradGradFunc ThresholdGradGradFuncObj;
  PReLUGradFunc PReLUGradFuncObj;
  GeLUGradFunc GeLUGradFuncObj;
  ReciprocalGradFunc ReciprocalGradFuncObj;
  LerpGradFunc LerpGradFuncObj;
  GmmV2BackwardGradFunc GmmV2BackwardGradFuncObj;
  AddbmmGradFunc AddbmmGradFuncObj;
  ReduceAllGradFunc ReduceAllGradFuncObj;
  SilentCheckV3GradFunc SilentCheckV3GradFuncObj;
  MaxPoolGradWithIndicesGradFunc MaxPoolGradWithIndicesGradFuncObj;
  LogSigmoidGradFunc LogSigmoidGradFuncObj;
  BatchNormGradExtGradFunc BatchNormGradExtGradFuncObj;
  PromptFlashAttentionGradFunc PromptFlashAttentionGradFuncObj;
  ArgMinExtGradFunc ArgMinExtGradFuncObj;
  UpsampleNearest2DGradGradFunc UpsampleNearest2DGradGradFuncObj;
  BitwiseOrScalarGradFunc BitwiseOrScalarGradFuncObj;
  SquareGradFunc SquareGradFuncObj;
  UpsampleBilinear2DGradGradFunc UpsampleBilinear2DGradGradFuncObj;
  PowScalarTensorGradFunc PowScalarTensorGradFuncObj;
  InplaceMulsGradFunc InplaceMulsGradFuncObj;
  InplaceExpGradFunc InplaceExpGradFuncObj;
  PReLUGradGradFunc PReLUGradGradFuncObj;
  InplaceRandomGradFunc InplaceRandomGradFuncObj;
  CopyGradFunc CopyGradFuncObj;
  ReduceMaxGradFunc ReduceMaxGradFuncObj;
  BatchNormExtGradFunc BatchNormExtGradFuncObj;
  GreaterEqualGradFunc GreaterEqualGradFuncObj;
  BitwiseAndScalarGradFunc BitwiseAndScalarGradFuncObj;
  BatchNormElemtGradFunc BatchNormElemtGradFuncObj;
  Log10GradFunc Log10GradFuncObj;
  SplitTensorGradFunc SplitTensorGradFuncObj;
  SwigluGradFunc SwigluGradFuncObj;
  MaskedFillGradFunc MaskedFillGradFuncObj;
  SoftmaxGradFunc SoftmaxGradFuncObj;
  CastGradFunc CastGradFuncObj;
  SearchSortedGradFunc SearchSortedGradFuncObj;
  IsNegInfGradFunc IsNegInfGradFuncObj;
  ReplicationPad3DGradFunc ReplicationPad3DGradFuncObj;
  GroupNormGradGradFunc GroupNormGradGradFuncObj;
  MaxPoolGradWithMaskGradFunc MaxPoolGradWithMaskGradFuncObj;
  AdaptiveMaxPool1DGradFunc AdaptiveMaxPool1DGradFuncObj;
  InplaceScatterAddGradFunc InplaceScatterAddGradFuncObj;
  SinhGradFunc SinhGradFuncObj;
  FmodScalarGradFunc FmodScalarGradFuncObj;
  ReflectionPad1DGradGradFunc ReflectionPad1DGradGradFuncObj;
  ContiguousGradFunc ContiguousGradFuncObj;
  RandnGradFunc RandnGradFuncObj;
  ReduceMinGradFunc ReduceMinGradFuncObj;
  InplaceIndexAddExtGradFunc InplaceIndexAddExtGradFuncObj;
  GeLUGradGradFunc GeLUGradGradFuncObj;
  InplaceSubExtGradFunc InplaceSubExtGradFuncObj;
  AddmvGradFunc AddmvGradFuncObj;
  UniqueDimGradFunc UniqueDimGradFuncObj;
  ZerosLikeExtGradFunc ZerosLikeExtGradFuncObj;
  LogAddExp2GradFunc LogAddExp2GradFuncObj;
  AdaptiveAvgPool3DExtGradFunc AdaptiveAvgPool3DExtGradFuncObj;
  L1LossExtGradFunc L1LossExtGradFuncObj;
  EyeGradFunc EyeGradFuncObj;
  UpsampleBilinear2DGradFunc UpsampleBilinear2DGradFuncObj;
  ErfGradFunc ErfGradFuncObj;
  SoftMarginLossGradGradFunc SoftMarginLossGradGradFuncObj;
  FlashAttentionScoreGradFunc FlashAttentionScoreGradFuncObj;
  InplaceClampTensorGradFunc InplaceClampTensorGradFuncObj;
  FloorDivScalarGradFunc FloorDivScalarGradFuncObj;
  UnstackExtGradFunc UnstackExtGradFuncObj;
  XlogyGradFunc XlogyGradFuncObj;
  RmsNormGradGradFunc RmsNormGradGradFuncObj;
  AddScalarGradFunc AddScalarGradFuncObj;
  NarrowGradFunc NarrowGradFuncObj;
  TakeGradFunc TakeGradFuncObj;
  BitwiseXorScalarGradFunc BitwiseXorScalarGradFuncObj;
  InplaceSubScalarGradFunc InplaceSubScalarGradFuncObj;
  BroadcastToGradFunc BroadcastToGradFuncObj;
  KLDivGradGradFunc KLDivGradGradFuncObj;
  BitwiseXorTensorGradFunc BitwiseXorTensorGradFuncObj;
  SqrtGradFunc SqrtGradFuncObj;
  AddExtGradFunc AddExtGradFuncObj;
  ReplicationPad2DGradGradFunc ReplicationPad2DGradGradFuncObj;
  InplaceZeroGradFunc InplaceZeroGradFuncObj;
  TriuGradFunc TriuGradFuncObj;
  MultinomialExtGradFunc MultinomialExtGradFuncObj;
  InnerIndexGradFunc InnerIndexGradFuncObj;
  InplaceClampScalarGradFunc InplaceClampScalarGradFuncObj;
  UpsampleNearest3DGradFunc UpsampleNearest3DGradFuncObj;
  ReflectionPad3DGradFunc ReflectionPad3DGradFuncObj;
  BitwiseAndTensorGradFunc BitwiseAndTensorGradFuncObj;
  BatchNormGatherStatsWithCountsGradFunc BatchNormGatherStatsWithCountsGradFuncObj;
  RandIntGradFunc RandIntGradFuncObj;
  TExtGradFunc TExtGradFuncObj;
  InplaceFloorDivideGradFunc InplaceFloorDivideGradFuncObj;
  ZerosGradFunc ZerosGradFuncObj;
  ReluGradGradFunc ReluGradGradFuncObj;
  RandnLikeGradFunc RandnLikeGradFuncObj;
  InplaceDivsGradFunc InplaceDivsGradFuncObj;
  SoftShrinkGradGradFunc SoftShrinkGradGradFuncObj;
  TanhGradFunc TanhGradFuncObj;
  BaddbmmGradFunc BaddbmmGradFuncObj;
  GmmBackwardGradFunc GmmBackwardGradFuncObj;
  IndexFillScalarGradFunc IndexFillScalarGradFuncObj;
  DivGradFunc DivGradFuncObj;
  SoftMarginLossGradFunc SoftMarginLossGradFuncObj;
  RepeatInterleaveIntGradFunc RepeatInterleaveIntGradFuncObj;
  UniqueConsecutiveGradFunc UniqueConsecutiveGradFuncObj;
  SiLUGradFunc SiLUGradFuncObj;
  VarMeanGradFunc VarMeanGradFuncObj;
  ErfinvGradFunc ErfinvGradFuncObj;
  SigmoidGradGradFunc SigmoidGradGradFuncObj;
  MaxGradFunc MaxGradFuncObj;
  AdaptiveAvgPool1DGradFunc AdaptiveAvgPool1DGradFuncObj;
  SubExtGradFunc SubExtGradFuncObj;
  DotGradFunc DotGradFuncObj;
  TileGradFunc TileGradFuncObj;
  Log2GradFunc Log2GradFuncObj;
  RepeatInterleaveGradGradFunc RepeatInterleaveGradGradFuncObj;
  CumsumExtGradFunc CumsumExtGradFuncObj;
  MedianExtGradFunc MedianExtGradFuncObj;
  Log1pGradFunc Log1pGradFuncObj;
  HistcExtGradFunc HistcExtGradFuncObj;
  MaxDimGradFunc MaxDimGradFuncObj;
  GluGradGradFunc GluGradGradFuncObj;
  SubGradFunc SubGradFuncObj;
  CloneGradFunc CloneGradFuncObj;
  InplaceMaskedFillTensorGradFunc InplaceMaskedFillTensorGradFuncObj;
  MedianDimGradFunc MedianDimGradFuncObj;
  UniformExtGradFunc UniformExtGradFuncObj;
  SignGradFunc SignGradFuncObj;
  TensorScatterElementsGradFunc TensorScatterElementsGradFuncObj;
  TruncGradFunc TruncGradFuncObj;
  NewOnesGradFunc NewOnesGradFuncObj;
  AvgPool2DGradFunc AvgPool2DGradFuncObj;
  LinalgQrGradFunc LinalgQrGradFuncObj;
  IndexFillTensorGradFunc IndexFillTensorGradFuncObj;
  IsFiniteGradFunc IsFiniteGradFuncObj;
  GLUGradFunc GLUGradFuncObj;
  InplaceMulGradFunc InplaceMulGradFuncObj;
  DiagExtGradFunc DiagExtGradFuncObj;
  SiLUGradGradFunc SiLUGradGradFuncObj;
  FlattenExtGradFunc FlattenExtGradFuncObj;
  Col2ImGradGradFunc Col2ImGradGradFuncObj;
  InplaceCopyGradFunc InplaceCopyGradFuncObj;
  LogicalNotGradFunc LogicalNotGradFuncObj;
  InnerInplaceIndexPutGradFunc InnerInplaceIndexPutGradFuncObj;
  KLDivGradFunc KLDivGradFuncObj;
  AtanExtGradFunc AtanExtGradFuncObj;
  StdMeanGradFunc StdMeanGradFuncObj;
  AdaptiveAvgPool2DExtGradFunc AdaptiveAvgPool2DExtGradFuncObj;
  UpsampleNearest3DGradGradFunc UpsampleNearest3DGradGradFuncObj;
  SpeedFusionAttentionGradFunc SpeedFusionAttentionGradFuncObj;
  Conv2DPaddingGradFunc Conv2DPaddingGradFuncObj;
  ClampScalarGradFunc ClampScalarGradFuncObj;
  RoundGradFunc RoundGradFuncObj;
  InplaceScatterSrcReduceGradFunc InplaceScatterSrcReduceGradFuncObj;
  InplaceScatterSrcGradFunc InplaceScatterSrcGradFuncObj;
  MishGradExtGradFunc MishGradExtGradFuncObj;
  UpsampleLinear1DGradGradFunc UpsampleLinear1DGradGradFuncObj;
  AcosExtGradFunc AcosExtGradFuncObj;
  FFNExtGradFunc FFNExtGradFuncObj;
  InplaceFillDiagonalGradFunc InplaceFillDiagonalGradFuncObj;
  FillTensorGradFunc FillTensorGradFuncObj;
  BinaryCrossEntropyGradFunc BinaryCrossEntropyGradFuncObj;
  CeilGradFunc CeilGradFuncObj;
  EluExtGradFunc EluExtGradFuncObj;
  SelectV2GradFunc SelectV2GradFuncObj;
  SeLUExtGradFunc SeLUExtGradFuncObj;
  EmbeddingDenseBackwardGradFunc EmbeddingDenseBackwardGradFuncObj;
  GatherDGradV2GradFunc GatherDGradV2GradFuncObj;
  AsinExtGradFunc AsinExtGradFuncObj;
  ConvolutionStrGradFunc ConvolutionStrGradFuncObj;
  SoftplusGradExtGradFunc SoftplusGradExtGradFuncObj;
  DropoutGradExtGradFunc DropoutGradExtGradFuncObj;
  InplaceIndexPutGradFunc InplaceIndexPutGradFuncObj;
  InplaceHardtanhGradFunc InplaceHardtanhGradFuncObj;
  SpeedFusionAttentionGradGradFunc SpeedFusionAttentionGradGradFuncObj;
  ReflectionPad1DGradFunc ReflectionPad1DGradFuncObj;
  ChunkGradFunc ChunkGradFuncObj;
  BCEWithLogitsLossGradFunc BCEWithLogitsLossGradFuncObj;
  ScatterValueGradFunc ScatterValueGradFuncObj;
  AvgPool3DGradExtGradFunc AvgPool3DGradExtGradFuncObj;
  RemainderTensorTensorGradFunc RemainderTensorTensorGradFuncObj;
  LinalgVectorNormGradFunc LinalgVectorNormGradFuncObj;
  NLLLoss2dGradFunc NLLLoss2dGradFuncObj;
  AdaptiveAvgPool3DGradExtGradFunc AdaptiveAvgPool3DGradExtGradFuncObj;
  InplaceEluGradFunc InplaceEluGradFuncObj;
  AddmmGradFunc AddmmGradFuncObj;
  InnerNonZeroGradFunc InnerNonZeroGradFuncObj;
  ConvolutionStrGradGradFunc ConvolutionStrGradGradFuncObj;
  BitwiseOrTensorGradFunc BitwiseOrTensorGradFuncObj;
  CumminExtGradFunc CumminExtGradFuncObj;
  PowTensorScalarGradFunc PowTensorScalarGradFuncObj;
  GreaterEqualScalarGradFunc GreaterEqualScalarGradFuncObj;
  SubScalarGradFunc SubScalarGradFuncObj;
  ConvolutionGradFunc ConvolutionGradFuncObj;
  MoeInitRoutingGradFunc MoeInitRoutingGradFuncObj;
  GroupedMatmulV2GradFunc GroupedMatmulV2GradFuncObj;
  DynamicQuantExtGradFunc DynamicQuantExtGradFuncObj;
  MoeComputeExpertTokensGradFunc MoeComputeExpertTokensGradFuncObj;
  QuantV2GradFunc QuantV2GradFuncObj;
  QuantBatchMatmulGradFunc QuantBatchMatmulGradFuncObj;
  MoeGatingTopKSoftmaxGradFunc MoeGatingTopKSoftmaxGradFuncObj;
  FusedInferAttentionScoreGradFunc FusedInferAttentionScoreGradFuncObj;
  MoeFinalizeRoutingGradFunc MoeFinalizeRoutingGradFuncObj;
  GroupedMatmulV4GradFunc GroupedMatmulV4GradFuncObj;
  KVCacheScatterUpdateGradFunc KVCacheScatterUpdateGradFuncObj;
  AddRmsNormQuantV2GradFunc AddRmsNormQuantV2GradFuncObj;
  GroupedMatmulGradFunc GroupedMatmulGradFuncObj;
  MoeInitRoutingV2GradFunc MoeInitRoutingV2GradFuncObj;
  WeightQuantBatchMatmulGradFunc WeightQuantBatchMatmulGradFuncObj;
  MatmulAllReduceAddRmsNormGradFunc MatmulAllReduceAddRmsNormGradFuncObj;
  PixelShuffleGradFunc PixelShuffleGradFuncObj;
};
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_MINDSPORE_OPS_KERNEL_FUNCTIONS_AUTO_GENERATE_AUTO_GRAD_OP_REG_H_
