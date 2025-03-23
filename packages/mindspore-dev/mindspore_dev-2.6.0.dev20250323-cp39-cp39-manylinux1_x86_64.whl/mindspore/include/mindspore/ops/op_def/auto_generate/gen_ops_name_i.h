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
constexpr auto kNameInplaceMul = "InplaceMul";
constexpr auto kNameInnerInplaceIndexPut = "InnerInplaceIndexPut";
constexpr auto kNameIDCT = "IDCT";
constexpr auto kNameInplaceUniform = "InplaceUniform";
constexpr auto kNameInplaceNormal = "InplaceNormal";
constexpr auto kNameInplaceHardtanh = "InplaceHardtanh";
constexpr auto kNameIsInf = "IsInf";
constexpr auto kNameInplaceFloorDivides = "InplaceFloorDivides";
constexpr auto kNameInplaceDivs = "InplaceDivs";
constexpr auto kNameInnerIndex = "InnerIndex";
constexpr auto kNameInplaceScatterAdd = "InplaceScatterAdd";
constexpr auto kNameInnerCommIrecv = "InnerCommIrecv";
constexpr auto kNameInplaceClampTensor = "InplaceClampTensor";
constexpr auto kNameInplaceMaskedFillTensor = "InplaceMaskedFillTensor";
constexpr auto kNameIFFT = "IFFT";
constexpr auto kNameInplaceDivMod = "InplaceDivMod";
constexpr auto kNameInplaceIndexPut = "InplaceIndexPut";
constexpr auto kNameInplaceThreshold = "InplaceThreshold";
constexpr auto kNameInplaceFillDiagonal = "InplaceFillDiagonal";
constexpr auto kNameInplaceDivMods = "InplaceDivMods";
constexpr auto kNameIndexFillTensor = "IndexFillTensor";
constexpr auto kNameInplaceAddmm = "InplaceAddmm";
constexpr auto kNameInnerNonZero = "InnerNonZero";
constexpr auto kNameInnerCommIsend = "InnerCommIsend";
constexpr auto kNameIRFFTDouble = "IRFFTDouble";
constexpr auto kNameInplaceIndexAddExt = "InplaceIndexAddExt";
constexpr auto kNameIndexAddExt = "IndexAddExt";
constexpr auto kNameIHFFTN = "IHFFTN";
constexpr auto kNameInplaceDiv = "InplaceDiv";
constexpr auto kNameIsNegInf = "IsNegInf";
constexpr auto kNameIDCTN = "IDCTN";
constexpr auto kNameInplaceErfinv = "InplaceErfinv";
constexpr auto kNameIndexFillScalar = "IndexFillScalar";
constexpr auto kNameIRFFT = "IRFFT";
constexpr auto kNameInplaceAddExt = "InplaceAddExt";
constexpr auto kNameInplaceExp = "InplaceExp";
constexpr auto kNameInplaceReLU = "InplaceReLU";
constexpr auto kNameInplaceScatterSrc = "InplaceScatterSrc";
constexpr auto kNameInplaceScatterValue = "InplaceScatterValue";
constexpr auto kNameInplaceRandom = "InplaceRandom";
constexpr auto kNameInplaceMaskedFillScalar = "InplaceMaskedFillScalar";
constexpr auto kNameInplacePut = "InplacePut";
constexpr auto kNameInnerCommAllGather = "InnerCommAllGather";
constexpr auto kNameInplaceFloor = "InplaceFloor";
constexpr auto kNameInnerCommReduceScatter = "InnerCommReduceScatter";
constexpr auto kNameIndex = "Index";
constexpr auto kNameInsertGemV2InBackward = "InsertGemV2InBackward";
constexpr auto kNameIHFFT = "IHFFT";
constexpr auto kNameInplaceStopGradient = "InplaceStopGradient";
constexpr auto kNameInplaceTanh = "InplaceTanh";
constexpr auto kNameInplaceFloorDivide = "InplaceFloorDivide";
constexpr auto kNameIndexSelect = "IndexSelect";
constexpr auto kNameInplaceZero = "InplaceZero";
constexpr auto kNameIFFTShift = "IFFTShift";
constexpr auto kNameInplaceElu = "InplaceElu";
constexpr auto kNameInplaceGroupedMatmulAdd = "InplaceGroupedMatmulAdd";
constexpr auto kNameIRFFTN = "IRFFTN";
constexpr auto kNameInplaceClampScalar = "InplaceClampScalar";
constexpr auto kNameInplaceScatterSrcReduce = "InplaceScatterSrcReduce";
constexpr auto kNameIFFTN = "IFFTN";
constexpr auto kNameInplaceSubScalar = "InplaceSubScalar";
constexpr auto kNameInplaceScatterValueReduce = "InplaceScatterValueReduce";
constexpr auto kNameIsFinite = "IsFinite";
constexpr auto kNameIsClose = "IsClose";
constexpr auto kNameInnerCommAllReduce = "InnerCommAllReduce";
constexpr auto kNameIHFFT2 = "IHFFT2";
constexpr auto kNameInplaceAddsExt = "InplaceAddsExt";
constexpr auto kNameInplaceCopy = "InplaceCopy";
constexpr auto kNameIFFT2 = "IFFT2";
constexpr auto kNameIm2ColExt = "Im2ColExt";
constexpr auto kNameIRFFT2 = "IRFFT2";
constexpr auto kNameIncreFlashAttention = "IncreFlashAttention";
constexpr auto kNameInplaceFillTensor = "InplaceFillTensor";
constexpr auto kNameInplaceMuls = "InplaceMuls";
constexpr auto kNameInplaceSubExt = "InplaceSubExt";
constexpr auto kNameInplaceFillScalar = "InplaceFillScalar";
constexpr auto kNameInplaceLog = "InplaceLog";
constexpr auto kNameInnerCommAllToAllV = "InnerCommAllToAllV";
constexpr auto kNameIdentity = "Identity";
}  // namespace mindspore::ops

#endif  // MINDSPORE_CORE_OP_NAME_I_H_
