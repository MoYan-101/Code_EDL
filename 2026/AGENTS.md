# 2026 Folder Memory

进入这个 `2026/` 文件夹后，先读这个文件。这里记录本目录下重要文件夹和这次对话形成的上下文，按“目录 - 具体内容”组织。

## ./ - 总体上下文

- 当前工作目录是 mixed-potential EDL 代码和图件工作区。
- 这里有一个外层 git repo，`Mixed_Potential_Electrical_Double_Layer/` 是内层 git submodule/repo。
- 不要误删或覆盖用户的 Word/Illustrator 文件。`MS/` 已在外层 repo 的本地 `.git/info/exclude` 里忽略；`Figures/Figure_1_v2.ai` 是用户打开的 AI 文件，不要碰，除非用户明确要求。
- 用户偏好：中文交流；代码/图件修改后给出具体路径；结果参数要能追溯到结果目录。

## Mixed_Potential_Electrical_Double_Layer/ - 模型代码与结果

- 主线性求解文件是 `Solve_Emix_updating.py`。
- `Solve_Emix_nonlinearPB.py` 是 nonlinear PB 版本；之前 review 时用户明确说“不用看 nonlinear part”。
- 线性模型核心包括 Debye-Huckel/linearized PB, Stern/linear charging BC, Frumkin-corrected Butler-Volmer kinetics, and mixed-potential root solve。
- 之前 review 的结论：主线性方程符号大体自洽；闭式解和 root solve 在默认参数下能对到机器精度；均一边界条件会退化到解析常数解。
- 重要 caveat：默认参数下 Debye-Huckel 适用性可能超限，self-check 曾给 `max |phi_tilde| = 5.4068`，高于默认阈值 1。

## Mixed_Potential_Electrical_Double_Layer/Solve_Emix_updating.py - 已修复事项

- 已修复 optional overrides 的 finite 检查：
  - `epsilon_s` 必须 finite 且 `> 0`。
  - `lambda_D` 必须 finite 且 `> 0`。
  - `g_Au/g_C/g_Pd` 必须 finite 且 `>= 0`。
- 该修复已验证：
  - 默认参数仍能通过 `validate_params()` 和 `compute_derived_params()`。
  - `lambda_D/epsilon_s/g_* = nan/inf/-inf` 会抛 `ValueError`。
  - `python3 -m py_compile Mixed_Potential_Electrical_Double_Layer/Solve_Emix_updating.py` 通过。

## Mixed_Potential_Electrical_Double_Layer/result_parameter_memory.md - 结果参数记忆

- 这个文件记录结果目录与参数的对应关系。
- 当前已记录 `results/20260528_111255/` 的参数、单位和自动推导值。
- 该结果对应：
  - `C_tot = 10 mM`
  - `lambda_D = 3.041 nm` auto-calculated
  - `L_Au / L_gap / L_Pd = 11 / 10 / 37 nm`
  - `out_of_plane_width = 1 cm`（从原先 unit width `1 m` 改为实际宽度；`i_mix_abs_A` 缩小 100 倍，`i_mix_avg_A_per_m2` 不变）
  - `Cdl_Au / Cdl_support / Cdl_Pd = 20 / 10 / 40 uF/cm^2`
  - `pzc_Au / pzc_support / pzc_Pd = 0.93 / 0.50 / 0.78 V`
  - `E1_eq / E2_eq = 0.10 / 0.834 V`
  - `pH = 7`
  - linear Debye-Huckel EDL, OFAT and heatmaps enabled。

## Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/ - 最新使用结果

- 这是目前用于图件和参数记忆的结果目录。
- 参数来源：`params.json`。
- mixed-potential 数值来源：`csv/summary_compare.csv`。
- 关键电压 vs RHE：
  - `E1_eq_eff = 0.100 V`
  - `E2_eq_eff = 0.834 V`
  - `E_mix_with = 0.6314371241995458 V`
  - `E_mix_no = 0.4915721295774951 V`
  - `pzc_C = 0.50 V`
  - `pzc_Pd = 0.78 V`
  - `pzc_Au = 0.93 V`
- 关键平均混合电流密度：
  - `i_mix_avg_with = 0.05449754430614139 A/m^2`
  - `i_mix_avg_no = 0.04153392038470155 A/m^2`
- 图中电压标注按用户要求保留两位小数。

## Figures/ - 手动图件与导出图

- 当前图件脚本都读取同一组可追溯输入：
  - `Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/params.json`
  - `Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/csv/summary_compare.csv`
- 电压相对位置图脚本：`Figures/make_potential_reference_map.py`。
- 电压相对位置图只导出：
  - `Figures/potential_reference_map_20260528_111255.png`
  - `Figures/potential_reference_map_20260528_111255.svg`
- 图中显示：
  - `E1_eq = 0.10 V`
  - `E_mix no EDL = 0.49 V`
  - `PZC support = 0.50 V`
  - `E_mix with EDL = 0.63 V`
  - `PZC Pd = 0.78 V`
  - `E2_eq = 0.83 V`
  - `PZC Au = 0.93 V`
- EDL-corrected BV mixed-potential 图脚本：`Figures/make_edl_bv_mixed_potential.py`。
  - 复用 `Solve_Emix_updating.compute_polarization_curve(...)`，`mode="FULL"`，`use_edl=True`。
  - 画 signed average half-reaction current density：Au anodic 为正，Pd cathodic 为负。
  - 导出：
    - `Figures/edl_bv_mixed_potential_20260528_111255.png`
    - `Figures/edl_bv_mixed_potential_20260528_111255.svg`
- EDL vs no-EDL BV 对比图脚本：`Figures/make_edl_vs_no_edl_bv_mixed_potential.py`。
  - `use_edl=True` 曲线用实线；`use_edl=False` 曲线用虚线。
  - 标出 `E_mix with EDL = 0.63 V` 和 `E_mix no EDL = 0.49 V`，并标出对应 `|i|`。
  - 当前版本按用户要求改成 Nature-style/clean paper figure 风格。
  - 字体栈为 `Helvetica, Nimbus Sans, Arial, DejaVu Sans, sans-serif`；本机没有真正 Helvetica，PNG 实际用 Helvetica-compatible `Nimbus Sans`，SVG 普通文字保留 Helvetica-first 字体栈且 `svg.fonttype="none"`。
  - 导出：
    - `Figures/edl_vs_no_edl_bv_mixed_potential_20260528_111255.png`
    - `Figures/edl_vs_no_edl_bv_mixed_potential_20260528_111255.svg`
- 带 PZC 的 EDL vs no-EDL BV 对比图脚本：`Figures/make_edl_vs_no_edl_bv_mixed_potential_with_pzc.py`。
  - 在 Nature-style EDL/no-EDL 对比图基础上增加 PZC lane。
  - PZC 标注为 `PZC support = 0.50 V`、`PZC Pd = 0.78 V`、`PZC Au = 0.93 V`。
  - 为显示 `PZC Au = 0.93 V`，横轴右端扩到约 `0.97 V`。
  - 主图中用淡金色竖虚线对齐 PZC 位置，下方用三角 marker 和文字标注 PZC。
  - 导出：
    - `Figures/edl_vs_no_edl_bv_mixed_potential_with_pzc_20260528_111255.png`
    - `Figures/edl_vs_no_edl_bv_mixed_potential_with_pzc_20260528_111255.svg`
- 用户明确要求不再生成 PDF；不要重新加入 PDF 输出。
- 不要碰 `Figures/Figure_1_v2.ai`，除非用户明确要求。

## Figures/Figure_3/ - 合格版 Figure 3 独立 panels

- 当前合格版 Figure 3 独立 panel 脚本是 `Figures/Figure_3/make_figure_3_panels.py`。
- 脚本固定读取可追溯输入：
  - `Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/params.json`
  - `Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/csv/summary_compare.csv`
- 脚本复用 `Solve_Emix_updating` 的主线性模型逻辑：
  - `run_edl_comparison_pair(params, mode="FULL")`
  - `build_profiles_for_emix(...)`
  - local concentration from `exp(-z_i * phi_tilde)`
  - local overpotential from `E_mix - E_eq_eff - phi_RP(x)`
  - local current density from profile `i1/i2` masks。
- 视觉规则：
  - `with EDL` 用亮暖色/red-orange family。
  - `without EDL` 用暗冷色/navy-blue family。
  - panel c 保持 log y-scale。
  - panel f 是 PZC + potential reference map，不是 BV+PZC current plot。
  - 图片内部已按用户要求删除 panel 字母；文件名仍保留 `panel_a` 等用于追溯，不代表图片里有字母。
- 只导出 PNG/SVG，不导出 PDF：
  - `figure_3_panel_a_emix_imix_20260528_111255.png/svg`
  - `figure_3_panel_b_reaction_plane_potential_20260528_111255.png/svg`
  - `figure_3_panel_c_local_reactant_concentration_20260528_111255.png/svg`
  - `figure_3_panel_d_local_overpotential_20260528_111255.png/svg`
  - `figure_3_panel_e_local_current_density_20260528_111255.png/svg`
  - `figure_3_panel_f_pzc_potential_reference_map_20260528_111255.png/svg`
- 已验证：
  - `python3 -m py_compile Figures/Figure_3/make_figure_3_panels.py` 通过。
  - 运行脚本会重新计算并断言 `E_mix` 和 `i_mix_avg` 与 `summary_compare.csv` 一致。
  - 输出数量为 6 PNG + 6 SVG + 0 PDF。
  - 抽查 panel c 和 panel f，图片内部没有 a-f panel 字母。
- 运行脚本时仍会出现已知 caveat warning：`max |phi_tilde| = 5.40679` 超过 Debye-Huckel 阈值 1；这是当前结果目录的模型适用性提醒，不是导出失败。

## Git 状态记忆

- 曾经清理过工作树：
  - 内层 repo 提交：`6b892ea Record result parameters and tighten validation`
  - 外层 repo 提交：`6649f9f Update EDL results submodule`
- 后续新增了 `Figures/` 下的 BV/EDL 图脚本、Figure 3 独立 panel 脚本和导出图；如果用户要求“清理工作树”，需要考虑是否提交 `Figures/` 和更新后的 `AGENTS.md`。
- 不要使用 destructive git 命令；不要 revert 用户未要求还原的文件。
