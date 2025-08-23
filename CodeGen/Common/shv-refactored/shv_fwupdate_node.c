/*
  COPYRIGHT (C) 2025  Stepan Pressl (press.stepan@gmail.com)

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
 */

#include <pyblock.h>
#include <shv/tree/shv_tree.h>
#include <shv/tree/shv_methods.h>
#include <shv/tree/shv_com.h>
#include <shv/tree/shv_file_com.h>
#include <ulut/ul_utdefs.h>

const shv_method_des_t * const shv_fwupdate_dmap_items[] =
{
  &shv_dmap_item_file_node_crc,
  &shv_dmap_item_dir,
  &shv_dmap_item_ls,
  &shv_dmap_item_file_node_size,
  &shv_dmap_item_file_node_stat,
  &shv_dmap_item_file_node_write
};

const shv_dmap_t shv_fwupdate_dmap =
{
  .methods =
  {
    .items = (void **)shv_fwupdate_dmap_items,
    .count = sizeof(shv_fwupdate_dmap_items)/sizeof(shv_fwupdate_dmap_items[0]),
    .alloc_count = 0,
  }
};
