/**
 * Copyright 2023-2025 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CORE_OP_NAME_I_H_
#define MINDSPORE_CORE_OP_NAME_I_H_

namespace mindspore::ops {
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceMul = "InplaceMul";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
