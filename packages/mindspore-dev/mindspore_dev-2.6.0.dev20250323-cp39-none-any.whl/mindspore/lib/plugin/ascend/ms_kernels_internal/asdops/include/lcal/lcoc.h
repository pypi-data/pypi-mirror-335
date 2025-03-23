/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef LCAL_LCOC_H
#define LCAL_LCOC_H

#include <lcal_comm.h>
#include <hccl.h>
#include "lcoc_args.h"
#include "tiling_args.h"

namespace Lcal {
struct CoCParamDesc {
    CoCDataTypeDesc dataTypeDesc = FP16FP16_FP32_FP16;
    MatMulInfo mmInfo = {};
    QuantInfo quantInfo = {};
    PostInfo postInfo = {};
    HcclReduceOp op = HCCL_REDUCE_SUM;  // 当前不支持其他值
    TwoDimTPInfo twoDimTPInfo = {};
};
struct CoCInputPkg {
    void *matrixA = nullptr;
    void *matrixB = nullptr;
    void *bias = nullptr;
    void *gamma = nullptr;
    void *dequantScale = nullptr;  // 反量化参数，当融合了Matmul前置伪量化或后置反量化操作时需要传入
    void *dequantOffset = nullptr;  // 可选，若无offset（如对称量化场景），传入空指针即可

    void *quantScale = nullptr;   // 量化参数，当融合了量化操作时需要传入
    void *quantOffset = nullptr;  // 可选，若无offset（如对称量化场景），传入空指针即可
};

struct CoCOutputPkg {
    void *output = nullptr;
    void *midOutput = nullptr;  // 先通信后计算情况下，通信的中间结果
};

class Lcoc {
public:
    Lcoc() = delete;
    explicit Lcoc(LcalComm &comm);
    explicit Lcoc(LcalComm *comm);
    ~Lcoc();
    int SetParam(LcalType lcalType, const CoCTiling &tiling, const CoCParamDesc &paramDesc);
    int All2AllMatmul(CoCInputPkg inputPkg, CoCOutputPkg outputPkg, void *workspace, aclrtStream stream = nullptr);
    int AllGatherMatmul(CoCInputPkg inputPkg, CoCOutputPkg outputPkg, void *workspace, aclrtStream stream = nullptr);
    int AllGatherMatmulV2(CoCInputPkg inputPkg, CoCOutputPkg outputPkg, void *workspace, aclrtStream stream = nullptr);
    int MatmulReduceScatter(CoCInputPkg inputPkg, CoCOutputPkg outputPkg, void *workspace,
                            aclrtStream stream = nullptr);
    int MatmulAllReduce(CoCInputPkg inputPkg, CoCOutputPkg outputPkg, void *workspace, aclrtStream stream = nullptr);
    int PureMatmul(CoCInputPkg inputPkg, CoCOutputPkg outputPkg, void *workspace, aclrtStream stream = nullptr);
    int AllGatherMatmulReduceScatter(CoCInputPkg inputPkg, CoCOutputPkg outputPkg,
                                     void *workspace, aclrtStream stream = nullptr);
    int64_t GetWorkspaceSize();
    LcalComm *GetComm();
    MatMulInfo &GetMatMulInfo();
    int32_t GetEleSize();
    void GetTiling(CoCTiling &tiling);

private:
    bool CheckDataType() const;
    bool InitTiling(const CoCTiling &tiling);
    int LaunchOperator(CoCInputPkg &inputPkg, CoCOutputPkg &outputPkg, void *workspace, aclrtStream stream);
    bool CheckBasic(const CoCInputPkg &inputPkg, const CoCOutputPkg &outputPkg, LcalType lcalType) const;

private:
    LcalComm *comm_ = nullptr;
    LcalType lcalType_ = LcalType::ALL_REDUCE;
    CoCParamDesc paramDesc_ = {};
    CoCTiling tiling_ = {};
    int rank_ = 0;
    int rankSize_ = 0;
    bool tilingSuccess_ = false;
};
WorkspaceDetail GetWorkspaceDetail(CoCDataTypeDesc dataType, const MatMulInfo &mmInfo, const QuantInfo &quantInfo);
}
#endif  // LCAL_LCOC_H
