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

## Figures/Figrue_RP/ - Figure 3 条件下的 2D Phi_s/reactants 图

- 当前脚本是 `Figures/Figrue_RP/make_phi_s_reactants_2d.py`。
- 固定读取：
  - `Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/params.json`
  - `Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/csv/summary_compare.csv`
- 图件参考 Huang et al. 2017 的 Figure 4 风格，但使用本模型 Figure 3 baseline 条件。
- `Phi_s(x,y)` 的来源：
  - 复用 `Solve_Emix_updating.EDLModel` 的 linear Debye-Huckel 展开。
  - `A = A_M * beta * E_mix_with - A_pzc`。
  - `phi_tilde(x,y) = sum_n A_n cos(rho_n x_tilde) exp(-gamma_n y_tilde)`。
  - `Phi_s [V] = (RT/F) * phi_tilde`，相对 bulk solution potential `phi_bulk = 0`。
- reactants 画归一化浓度：
  - `c_R1/c_bulk = exp(-z_R1 * phi_tilde)`。
  - `c_O2/c_bulk = exp(-z_O2 * phi_tilde)`。
- 空间范围：
  - baseline: `x = 0-58 nm`，Au/support/Pd = `0-11/11-21/21-58 nm`。
  - `y = 0-5 lambda_D = 0-15.21 nm`。
- 只导出：
  - `Figures/Figrue_RP/phi_s_reactants_2d_20260528_111255.png`
  - `Figures/Figrue_RP/phi_s_reactants_2d_20260528_111255.svg`
- 已验证 `y=0` 的 `Phi_s(x,0)` 与 Figure 3 panel b 的 `phi_RP(x)` 一致。

## Figures/Figure_same_length/ - Au/Pd 等长图件集

- 目录是 `Figures/Figure_same_length/`，镜像结构：
  - `Figure_3/`
  - `Figure_scheme/`
  - `Figrue_RP/`
  - `inputs/`
- 共享 helper：`Figures/Figure_same_length/same_length_common.py`。
- 参数从 `results/20260528_111255/params.json` 读取，并 override：
  - `L_Au = 25 nm`
  - `L_Pd_len = 25 nm`
  - 其他参数保持 baseline，包括 `L_gap = 10 nm` 和 `C_tot = 10 mM`。
- 输出 tag：`same_length_au25_pd25_20260528_111255`。
- 只导出 PNG/SVG，不导出 PDF；`Figure_scheme` 只生成带 PZC 的 EDL vs no-EDL BV 图。
- 关键结果：
  - `E_mix_with ≈ 0.6127292792 V`
  - `E_mix_no ≈ 0.4557694001 V`
  - `i_mix_avg_with ≈ 0.0608919385 A/m^2`
  - `i_mix_avg_no ≈ 0.0451292034 A/m^2`
  - `lambda_D = 3.041217889 nm`
  - `L_total = 60 nm`
- 对比 baseline 时，长度变化对 `E_mix` 的影响不大，原因是原 baseline 中 Pd 区域较长且 EDL/frumkin 权重使 Pd cathodic contribution 占优；改成等长后仍保留明显 EDL-induced shift。

## Figures/Figure_same_length_i0/ - Au/Pd 等长 + 等 i0 图件集

- 目录是 `Figures/Figure_same_length_i0/`，镜像结构：
  - `Figure_3/`
  - `Figure_scheme/`
  - `Figrue_RP/`
  - `inputs/`
- 共享 helper：`Figures/Figure_same_length_i0/same_length_i0_common.py`。
- 参数 override：
  - `L_Au = 25 nm`
  - `L_Pd_len = 25 nm`
  - `it0_1 = it0_2 = sqrt(8.85e-5 * 3.878e-4) = 1.852573885166257e-4 A/m^2`
  - 其他参数保持 baseline。
- 输出 tag：`same_length_i0_geom_au25_pd25_20260528_111255`。
- 只导出 PNG/SVG，不导出 PDF；`Figure_scheme` 只生成带 PZC 的 EDL vs no-EDL BV 图。
- 关键结果：
  - `E_mix_with ≈ 0.5873998539 V`
  - `E_mix_no ≈ 0.4121609195 V`
  - `i_mix_avg_with ≈ 0.0620782271 A/m^2`
  - `i_mix_avg_no ≈ 0.0404126392 A/m^2`
  - `max |phi_tilde| ≈ 6.23139`

## Figures/Figure_same_length_i0_alpha/ - Au/Pd 等长 + 等 i0 + alpha=0.5 图件集

- 目录是 `Figures/Figure_same_length_i0_alpha/`，镜像结构：
  - `Figure_3/`
  - `Figure_scheme/`
  - `Figrue_RP/`
  - `Heatmap/`
  - `inputs/`
- 共享 helper：`Figures/Figure_same_length_i0_alpha/same_length_i0_alpha_common.py`。
- 参数从 `results/20260528_111255/params.json` 读取，并 override：
  - `L_Au = 25 nm`
  - `L_Pd_len = 25 nm`
  - `it0_1 = it0_2 = 1.852573885166257e-4 A/m^2`
  - `alpha1 = alpha2 = 0.5`
  - `out_of_plane_width = 0.01 m`
  - 其他参数保持 baseline，包括 `L_gap = 10 nm`、`C_tot = 10 mM`、PZC、Cdl、charges、pH。
- 输出 tag：`same_length_i0_alpha050_au25_pd25_20260528_111255`。
- 一键入口：`Figures/Figure_same_length_i0_alpha/make_all_same_length_i0_alpha.py`。
- 只导出 PNG/SVG，不导出 PDF；`Figure_scheme` 只生成带 PZC 的 EDL vs no-EDL BV 图。
- 关键结果：
  - `E_mix_with = 0.5979829354430014 V`
  - `E_mix_no = 0.4670000000000001 V`
  - `i_mix_avg_with = 0.08384634584416407 A/m^2`
  - `i_mix_avg_no = 0.11756035407872442 A/m^2`
  - `i_mix_abs_with = 4.192317292208204e-11 A`
  - `i_mix_abs_no = 5.878017703936221e-11 A`
  - `lambda_D = 3.041217889 nm`
  - `max |phi_tilde| = 6.038944611092431`
- 该条件下即使 `L/i0/alpha` 都相同，with EDL 和 without EDL 的 `E_mix` 仍相差约 `0.131 V`。原因不是几何或 i0，而是 EDL 改变了 reaction-plane potential 和局部反应物浓度：BV 局部过电位含 `E_mix - E_eq - phi_RP(x)`，浓度含 `exp(-z_i * phi_tilde)`，因此 Frumkin/Boltzmann 权重会强烈改变 Au/Pd 两个 half-reaction 的相对强度。

## Figures/Figure_same_length_i0_alpha/Heatmap/ - 等长等 i0 等 alpha baseline 的 heatmap

- 当前脚本是 `Figures/Figure_same_length_i0_alpha/Heatmap/make_heatmap_combined_panel_log_same_length_i0_alpha.py`。
- 使用 `same_length_i0_alpha_common.py` 读取和校验 baseline，不改 `Solve_Emix_updating.py`。
- 只生成 log combined panel，不生成 linear 版，不生成 PDF。
- 主图输出：
  - `Figures/Figure_same_length_i0_alpha/Heatmap/heatmap_combined_panel_log.png`
  - `Figures/Figure_same_length_i0_alpha/Heatmap/heatmap_combined_panel_log.svg`
- 支撑数据：
  - `Figures/Figure_same_length_i0_alpha/Heatmap/csv/`
  - 共 30 个 `heatmap_compare_*.csv`。
  - `inputs/` 中保存该 heatmap 使用的 params、overrides、summary。
- 三组 25 x 25 扫描：
  - `pzc_Au × pzc_Pd`：linear，baseline PZC ± `heatmap_pzc_span`。
  - `Cdl_Au × Cdl_Pd`：log，`heatmap_Cdl_C_min` 到 `heatmap_Cdl_C_max`。
  - `L_Au × L_Pd_len`：log，`heatmap_L_min` 到 `heatmap_L_max`。
- 当前 heatmap 的定量结论：
  - 对 `i_mix_avg_with` 最重要的是 PZC，尤其 `pzc_Pd`；`pzc_Au × pzc_Pd` 扫描中电流约 `0.0039 -> 1.897 A/m^2`，约 `484x`。
  - 对 `E_mix_with`，PZC 和长度都重要；`pzc_Au × pzc_Pd` 总跨度约 `208 mV`，`L_Au × L_Pd` 总跨度约 `214 mV`。
  - `Cdl_Au × Cdl_Pd` 影响较次要，但不可忽略；`E_mix_with` 总跨度约 `116 mV`，`i_mix_avg_with` 约 `25x`。
  - baseline 附近单参数截线中，`pzc_Pd` 对电流最敏感；`pzc_Pd` 改变时 `i_mix` 约 `32x`，`pzc_Au` 约 `15x`，长度单参数约 `3x`。

## Git 状态记忆

- 曾经清理过工作树：
  - 内层 repo 提交：`6b892ea Record result parameters and tighten validation`
  - 外层 repo 提交：`6649f9f Update EDL results submodule`
- 后续新增了 `Figures/` 下的 BV/EDL 图脚本、Figure 3 独立 panel 脚本和导出图；如果用户要求“清理工作树”，需要考虑是否提交 `Figures/` 和更新后的 `AGENTS.md`。
- 不要使用 destructive git 命令；不要 revert 用户未要求还原的文件。
