/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <filesystem>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace iprm {
static const std::string FILE_NAME = "build.iprm";

class Object;

class Session {
 public:
  static void create(const std::string& root_dir);

  static void destroy();

  static void register_object(const std::shared_ptr<Object>& obj);

  static void begin_file_context(const std::string& entry_file_path);

  static void end_file_context();

  static std::shared_ptr<Object> get_object(const std::string& obj_name);

  static std::unordered_map<std::string, std::vector<std::shared_ptr<Object> > >
  get_objects();

  static void register_rename(const std::string& new_name,
                              const std::shared_ptr<Object>& stale_obj);

  static std::vector<std::string> retrieve_loadable_files();

  static std::string root_relative_source_dir();

  // NOTE: Only public so we can use a std::unique_pt as the static member var
  // instead of raw pointer
  explicit Session(const std::string& root_dir);

 private:
  std::filesystem::path root_dir_;
  static std::unique_ptr<Session> instance_;

  void register_object_impl(const std::shared_ptr<Object>& obj);

  void begin_file_context_impl(const std::string& entry_file_path);

  void end_file_context_impl();

  std::shared_ptr<Object> get_object_impl(const std::string& obj_name) const;

  std::unordered_map<std::string, std::vector<std::shared_ptr<Object> > >
  get_objects_impl() const;

  void register_rename_impl(const std::string& new_name,
                            const std::shared_ptr<Object>& stale_obj);

  std::vector<std::string> retrieve_loadable_files_impl() const;

  std::string root_relative_source_dir_impl() const;

  // Session overview:
  //  1. The file system graph collects all the supported project files
  //      starting from the root directory. Only native IPRM
  //      files will be acknowledged/supported as loadable files
  //  2. The session objects get created when python loaders execute the
  //      project files, they can then request data from the session about
  //      the files that exist and their paths
  //  3. After the objects are loaded, the main purpose until the session
  //      ends is to just keep objects alive while python generators emit
  //      their content or query information about the project state

  // Session Objects

  // Objects are only created if they are being loaded into memory by running a
  // python script, when that occurs, we should capture as much useful context
  // as possible, in this case, which file a particular object is an associated
  // with. this can help consumers with fast lookup of all the objects for a
  // particular file
  std::optional<std::filesystem::path> active_file_ctx_;

  // Owning references to the objects created. All consumers should retrieve
  // copies to objects from the Session, never creating their own uniquely owned
  // objects. Objects are grouped by the file that created them as that is
  // useful context for generators
  std::unordered_map<std::string, std::vector<std::shared_ptr<Object> > >
      objects_;
};
}  // namespace iprm
