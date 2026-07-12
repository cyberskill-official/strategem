"""Closed node/edge taxonomy — FR-KB-001."""

from __future__ import annotations

from enum import StrEnum


class NodeKind(StrEnum):
    thien_can = "thien_can"
    dia_chi = "dia_chi"
    giap_ty = "giap_ty"
    ngu_hanh = "ngu_hanh"
    bat_quai = "bat_quai"
    cuu_cung = "cuu_cung"
    thien_tuong = "thien_tuong"
    cuu_tinh = "cuu_tinh"
    bat_mon = "bat_mon"
    bat_than = "bat_than"
    than_16 = "than_16"
    cach_cuc = "cach_cuc"
    khoa_the = "khoa_the"
    than_sat = "than_sat"


class EdgeRel(StrEnum):
    sinh = "sinh"
    khac = "khac"
    hinh = "hinh"
    xung = "xung"
    pha = "pha"
    hai = "hai"
    hop = "hop"
    ky_cung = "ky_cung"
    lac_cung = "lac_cung"
    lam = "lam"
    thua = "thua"
    trang_thai = "trang_thai"
