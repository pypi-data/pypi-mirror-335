/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef LCAL_TILING_910B_H
#define LCAL_TILING_910B_H

#include "tiling_args.h"
namespace Lcal {
    void AllGatherGetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);
    void AllGatherEightRankFP16GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);

    void AllGatherV2EightRankFP16GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);
    void AllGatherV2EightRankFP16Core16GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);

    void AllReduceGetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);
    void AllReduceFourRankInt8GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);
    void AllReduceFourRankFP16GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);
    void AllReduceEightRankFP16GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);
    void AllReduceEightRankINT8GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);

    void ReduceScatterEightRankFP16GetDefaultTiling(PPTilingData &ppTilingData, CommTilingData &commTilingData);
}
#endif // LCAL_TILING_910B_H