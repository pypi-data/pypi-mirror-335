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
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
