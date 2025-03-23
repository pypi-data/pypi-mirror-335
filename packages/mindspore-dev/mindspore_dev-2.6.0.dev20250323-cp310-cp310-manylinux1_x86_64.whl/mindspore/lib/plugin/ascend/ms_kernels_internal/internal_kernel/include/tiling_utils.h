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

#ifndef MS_KERNELS_INTERNAL_KERNEL_TILING_UTILS_H_
#define MS_KERNELS_INTERNAL_KERNEL_TILING_UTILS_H_

#include <cstdint>
#include <functional>
#include <memory>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

#include "include/internal_op.h"

namespace mindspore {
namespace internal {
void Encrypt(char **src, size_t str_len, char *dest, bool offset_src = false);
void Decrypt(char **src, size_t str_len, char *dest, bool offset_src = true);

struct ScopeData {
  uint32_t begin;
  uint32_t end;
  uint32_t offset;
  uint32_t num;
};

struct ScopeInfo {
  std::vector<uint16_t> types;
  std::vector<ScopeData> scopes;
};

struct TilingData {
  uint16_t version;
  uint32_t base_offset;
  uint16_t key_len;
  uint16_t value_len;
  uint32_t item_num;
  uint16_t type_len;
  std::vector<ScopeInfo> scope_infos;
};

template <typename T>
struct ArrayHasher {
  std::size_t operator()(const std::vector<T> &arr) const {
    std::size_t hash = 0;
    for (T num : arr) {
      hash ^= std::hash<T>{}(num) + 0x9e3779b9 + (hash << 6) + (hash >> 2);
    }
    return hash;
  }
};

using Repo = std::unordered_map<std::vector<int>, std::vector<int>, ArrayHasher<int>>;
using RepoMap = std::unordered_map<std::vector<uint16_t>, Repo, ArrayHasher<uint16_t>>;

class TilingLoadUtil {
 public:
  explicit TilingLoadUtil(const std::string &db_file, bool is_full_path = false)
      : db_file_(db_file), is_full_(is_full_path) {}
  ~TilingLoadUtil();
  InternalStatus LoadTilingData(TilingData *tiling_data_out);
  InternalStatus LoadScopeTilings(uint32_t base, uint16_t key_len, uint16_t value_len, const ScopeData &scope, Repo *repo);

 private:
  std::string GetDataFileFullPath(const std::string &db_name) const;
  InternalStatus InitData();
  InternalStatus ReadTilingData(TilingData *tiling_data);
  InternalStatus ReadScopeData(TilingData *tiling_data);

  std::string db_file_;
  bool is_full_;
  int f_{-1};
  size_t memory_size_{0};
  char *data_{nullptr};
};

using KeyScope = std::pair<int, int>;

class TilingRepo {
 public:
  TilingRepo(const TilingRepo &flags) = delete;
  TilingRepo(TilingRepo &&flags) = delete;
  TilingRepo &operator=(const TilingRepo &flags) = delete;
  TilingRepo &operator=(TilingRepo &&flags) = delete;
  ~TilingRepo() = default;

  static TilingRepo &Instance();
  void Register(const std::string &name, const std::string &db_name);
  InternalStatus GetTiling(const std::string &name, const std::vector<uint16_t> &types, const std::vector<int> &key,
                       std::vector<int> *out,
                       const std::function<KeyScope(const std::vector<int> &)> &gen_scope_func = nullptr);
  using LoadRecord = std::unordered_map<std::vector<uint16_t>, std::vector<KeyScope>, ArrayHasher<uint16_t>>;

 private:
  TilingRepo() = default;
  bool IsRegistered(const std::string &name) const;
  std::vector<int> Get(const std::string &name, const std::vector<uint16_t> &types, const std::vector<int> &key) const;
  InternalStatus LoadScopeData(const std::string &name, const std::vector<uint16_t> &types,
                           const KeyScope &scope = std::make_pair(0, 0));

  std::unordered_map<std::string, size_t> name_idx_map_;
  std::unordered_map<std::string, size_t> db_name_idx_map_;
  std::vector<std::string> db_names_;
  std::vector<TilingData> tiling_datas_;
  std::vector<RepoMap> repo_maps_;
  std::vector<LoadRecord> loaded_;
};

class TilingDBLoad {
 public:
  TilingDBLoad(const std::string &op_name, const std::string &db_name) {
    TilingRepo::Instance().Register(op_name, db_name);
  }
};

struct RuningInfo {
  internal::ShapeInfoList input_shapes;
  internal::InputsImmutableInfoList input_infos;
  internal::ShapeInfoList output_shapes;
  internal::InputsImmutableInfoList output_infos;
};

class Tunable {
 public:
  Tunable() = default;
  virtual ~Tunable() = default;
  virtual InternalOpPtr CreateOpByKey(const std::vector<int64_t> &key) = 0;
  virtual RuningInfo GetRuningInfo(const std::vector<int64_t> &key) const = 0;
};
using TunablePtr = std::shared_ptr<Tunable>;

using TunableCreator = std::function<TunablePtr()>;
class TunableBuilder {
 public:
  ~TunableBuilder() = default;
  TunableBuilder(const TunableBuilder &) = delete;
  TunableBuilder &operator=(const TunableBuilder &) = delete;
  static TunableBuilder &Instance();

  void Register(const std::string &op_name, TunableCreator &&creator);
  TunablePtr Create(const std::string &op_name) const;

 private:
  TunableBuilder() = default;
  std::unordered_map<std::string, TunableCreator> tunable_creators_;
};

class TuneRegister {
 public:
  TuneRegister(const std::string &op_name, TunableCreator creator) noexcept {
    TunableBuilder::Instance().Register(op_name, std::move(creator));
  }
  ~TuneRegister() = default;
};

#define REG_OP_TUNABLE(op_name, TargetClass)                                                                  \
  static_assert(std::is_base_of<Tunable, TargetClass>::value, #TargetClass " must be derived from Tunable!"); \
  static const TuneRegister g_##op_name##_tunable_reg(#op_name,                                               \
                                                      []() -> TunablePtr { return std::make_shared<TargetClass>(); })
}  // namespace internal
}  // namespace mindspore

#endif  // MS_KERNELS_INTERNAL_KERNEL_TILING_UTILS_H_