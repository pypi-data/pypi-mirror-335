/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef LCAL_TILING_ARGS_H
#define LCAL_TILING_ARGS_H

#include "lcoc_base.h"

#pragma once
namespace Lcal {
    constexpr int32_t MAX_CORE_NUM = 20;
    constexpr int32_t MAX_L2_SIZE = 192 * 1024 * 1024;
    constexpr int32_t MAX_L0CSIZE = 128 * 1024;
    constexpr int32_t HBM_BM = 1;
    constexpr int32_t L2_BW = 5;
    constexpr int32_t BYTE_512 = 512;
    constexpr int32_t MAX_UB_NUM = 97280; // 190 * 1024 / 2
    constexpr int32_t MIN_UB_NUM = 256;
    constexpr int32_t P_VALUE = 8;
    constexpr int32_t MAX_P_VALUE = 15;
    constexpr int32_t TAG_MOD = 10000;
    constexpr int32_t SWIZZLE_COUNT_FOUR = 4;
    constexpr int32_t DEFAULT_SWIZZLE_COUNT = 7;
    constexpr int32_t SWIZZLE_DIRECT_ZERO = 0;
    constexpr int32_t SWIZZLE_DIRECT_ONE = 1;
    constexpr int32_t COMM_DATA_DIRECT = 0;
    constexpr int32_t COMM_NPU_DIRECT = 1;
    constexpr int32_t COMMNPUSPLIT_ONE = 1;
    constexpr int32_t COMMNPUSPLIT_THREE = 3;
    constexpr int32_t COMMNPUSPLIT_EIGHT = 8;
    constexpr int32_t COMMNPUSPLIT_FOUR = 4;
    constexpr int32_t COMMDATASPLIT_ONE = 1;
    constexpr int32_t COMMDATASPLIT_TWO = 2;
    constexpr int32_t COMMDATASPLIT_FOUR = 4;
    constexpr int32_t COMMDATASPLIT_EIGHT = 8;
    constexpr int32_t COMMDATASPLIT_SIXTEEN = 16;
    constexpr int32_t FLAG_BUFF_BYTES = 512 * 1024;  // 0.5MB
    constexpr int32_t AXES_ALIGN_SIZE_INT8 = 128;
    constexpr int32_t DEFAULT_ROW = 128;
    constexpr int32_t DEFAULT_COL = 256;
    constexpr int32_t AXES_ALIGN_SIZE = 512;
    constexpr int32_t BASE_BLOCK_STEP = 2;
    constexpr int32_t INPUT_DTYPE = 2;
    constexpr int32_t MAX_BLOCK_COUNT = 2;
    constexpr int32_t FP16_SIZE = 2;
    constexpr int32_t FP32_SIZE = 4;
    constexpr int32_t BLOCK_SIZE = 16;
    constexpr int32_t BLOCK_SIZE_K = 32;
    constexpr int32_t ND_SHAPE_SIZE = 2;
    constexpr int32_t NZ_SHAPE_SIZE = 4;
    constexpr int32_t CUBE_BLOCK_SIZE_INT8 = 512;
    constexpr int32_t CUBE_BLOCK_SIZE = 256;
    constexpr int32_t MIN_UB_MOVE_NUM = 5120;
    constexpr int32_t VALID_UB_MOVE_NUM = 20480;
    constexpr int32_t L1AB_PINGPONG_BUFFER_LEN_FP16 = 131072;  // 128 KB
    constexpr int32_t RATIO = 2000;
    constexpr int32_t CRITICAL_K = 2048;
    constexpr int32_t HALF_KBYTE = 512;
    constexpr int32_t SECOND_TO_MS = 1e3;
    constexpr int64_t MATMUL_BASE_100US = static_cast<int64_t>(1024) * 8192 * 1024;
    constexpr int64_t ALLREDUCE_BASE_100US = 4096 * 1024;
    constexpr double ONE_K = 1024.0;
    constexpr double B1_FLOP_PER_MS = (364 * 0.8) * 1e9;
    constexpr double DOUBLE = 2.0;
    constexpr double HALF_PROB = 0.5;
    constexpr int32_t CONDITION_M_ST = 0;
    constexpr int32_t CONDITION_M_END = 1;
    constexpr int32_t CONDITION_K_ST = 2;
    constexpr int32_t CONDITION_K_END = 3;
    constexpr int32_t CONDITION_N_ST = 4;
    constexpr int32_t CONDITION_N_END = 5;
    constexpr int32_t RANKSIZE_FOUR = 4;
    constexpr int32_t RANKSIZE_EIGHT = 8;
    constexpr int32_t RANKSIZE_SIXTEEN = 16;
    constexpr int32_t DIV_TWO = 2;
    constexpr int32_t LENPERLOOP_DEFAULT = 5120;
    constexpr int32_t ALLGATHERV2_CORENUM_SIXTEEN = 16;
    constexpr int32_t ALLREDUCE_LENPERLOOP_DEFAULT = 5120; // 使用的core数为16时的取值
    constexpr int32_t ALLREDUCE_UBMOVENUM_DEFAULT = 10;
    constexpr int32_t TREE_LEN_PER_LOOP = 20480;
    constexpr int32_t MAX_K_VALUE = 100000;
    constexpr int32_t MAX_N_VALUE = 100000;
    constexpr int32_t DIM_EIGHT = 8;
    constexpr int32_t DIM_TWO = 2;

    struct CoCTiling {
        int32_t m0 = -1;
        int32_t k0 = -1;
        int32_t n0 = -1;
        int32_t swizzlDirect = -1;
        int32_t swizzlCount = -1;
        int32_t splitK = -1;
        int32_t ubMoveNum = -1;
        int32_t pValue = -1;
        int32_t write2OtherRank = -1;
        int32_t blockDim = -1;
        int32_t withSerialMode = -1;
        int32_t commNpuSplit = -1;
        int32_t commDataSplit = -1;
        int32_t commDirect = -1;
        int32_t lenPerLoop = -1;
        int32_t extraUbMoveNum = -1;
        int32_t extraCommNpuSplit = -1;  // 2dtp使用
        int32_t extraCommDataSplit = -1;  // 2dtp使用
        int32_t extraCommDirect = -1;  // 2dtp使用
        int32_t extraLenPerLoop = -1;  // 2dtp使用
        int32_t is91093 = -1;
    };

    struct OpShape {
        int32_t batchSize = 1;
        int32_t m = -1;
        int32_t k = -1;
        int32_t n = -1;
        const char* ToString();
    };

    struct PPTilingData {
        OpShape opShape = {};
        int32_t m0 = 1;
        int32_t k0 = 1;
        int32_t n0 = 1;
        int32_t mLoop = 1;
        int32_t kLoop = 1;
        int32_t nLoop = 1;
        int32_t coreLoop = 1;
        int32_t swizzlCount = 1;
        int32_t swizzlDirect = 0;
        uint32_t tilingKey = 0;
        int32_t blockDim = 1;
        int32_t splitK = 0;

        void SetDefault(int32_t coreNum);
        void SetBaseShape(int32_t batchSize, int32_t m, int32_t k, int32_t n);
        void SetBaseOp(int32_t mBase, int32_t nBase);
        void SetTilingKey(const MatMulInfo &mmInfo);
        void Update(const MatMulInfo &mmInfo);
        void Swizzl();
        const char* ToString();
    };

    struct CommTilingData {
        int32_t rank = 1;
        int32_t rankSize = 1;
        int32_t pValue = 1;
        int32_t ubMoveNum = 1;
        int32_t write2OtherRank = 0;
        int32_t withSerialMode = 0;
        int32_t tag = 0;
        int32_t commNpuSplit = 1;
        int32_t commDataSplit = 1;
        int32_t commDirect = 0;
        int32_t lenPerLoop = 1;
        int32_t extraUbMoveNum = -1;
        int32_t extraCommNpuSplit = -1;  // 2dtp使用
        int32_t extraCommDataSplit = -1;  // 2dtp使用
        int32_t extraCommDirect = -1;  // 2dtp使用
        int32_t extraLenPerLoop = -1;  // 2dtp使用
        int32_t is91093 = 0;
        const char* ToString();
    };

    struct CoCTilingData {
        PPTilingData ppTilingData{};
        CommTilingData commTilingData{};
        void UpdateAssignedTiling(CoCTiling &tiling, const MatMulInfo &mmInfo);
        void SetBasicForTiling(const MatMulInfo &mmInfo, int32_t rank, int32_t rankSize);
        const char* ToString();
    };

    struct CoCKernelParam {
        CoCTilingData cocTilingData = {};
        QuantInfo quantInfo = {}; // device侧对应23-26
        TwoDimTPInfo twoDimTPInfo = {}; // device侧对应27-29
        PostInfo postInfo = {}; // device侧对应30
        bool weightNz = false;
    };
}
#endif // LCAL_TILING_ARGS_H