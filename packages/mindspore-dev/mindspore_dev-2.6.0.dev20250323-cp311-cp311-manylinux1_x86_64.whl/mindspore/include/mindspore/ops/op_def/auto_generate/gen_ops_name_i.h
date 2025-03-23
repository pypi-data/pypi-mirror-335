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
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameIndex = "Index";
constexpr auto kNameIdentity = "Identity";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameInplaceZero = "InplaceZero";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
