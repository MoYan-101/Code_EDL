# 2026 Folder Memory

进入这个 `2026/` 文件夹后，先读这个文件。这里记录本目录下重要文件夹和这次对话形成的上下文，按“目录 - 具体内容”组织。

## ./ - 总体上下文

- 当前工作目录是 mixed-potential EDL 代码和图件工作区。
- 这里有一个外层 git repo，`Mixed_Potential_Electrical_Double_Layer/` 是内层 git submodule/repo。
- 不要误删或覆盖用户的 Word/Illustrator 文件。`MS/` 已在外层 repo 的本地 `.git/info/exclude` 里忽略；`Figures/Figure_1_v2.ai` 是用户打开的 AI 文件，不要碰，除非用户明确要求。
- 用户偏好：中文交流；代码/图件修改后给出具体路径；结果参数要能追溯到结果目录。
- 画图 skill 使用约定：
  - 普通 matplotlib 数据图、bar/line/heatmap/multi-panel 优先用 `scientific-figure-making`。
  - 只有用户明确要求 “Nature-style chemistry figure / 用 nature 风格出图 / chemistry paper figure” 时再用 `chem-figure-style`。
  - `imagegen` 只用于生成/编辑位图插图，不替代科研数据图。
- 项目图件字体统一标准：优先使用 `Helvetica, Nimbus Sans, Arial, DejaVu Sans, sans-serif`。SVG 保留 Helvetica-first 字体栈；本机 PNG 若无 Helvetica 则用 Nimbus Sans/Arial/DejaVu Sans。
- 电位横轴统一写法优先用 `Potential (V vs. RHE)`，不要再写 `Potential vs RHE (V)`。
- `Figures/` 下图件的坐标轴、colorbar 和图面单位统一用圆括号，例如 `x (nm)`、`Phi_s (mV)`、`Current (10^-3 uA)`；不要在图面单位中使用方括号。
- 修改已有科研图件版式时，优先修改生成脚本中的常量、layout 或 label 并重新导出 PNG/SVG；不要直接手改 SVG，除非用户明确要求只编辑某个 SVG 文件。
- 图件导出默认保持 PNG/SVG，不新增 PDF；如果脚本需要重跑，重跑后确认没有 PDF 和多余 `__pycache__` 作为交付内容。
- 从 Figure 5 起，图面、legend、标题、文档说明和新输出文件名中的双电层/Helmholtz 电容显示名统一用 `C_H`，不要再使用旧电容显示记号；内部 solver 参数、CSV 兼容字段和旧输入键仍保留 `Cdl_Au`、`Cdl_C`、`Cdl_Pd`。
- EDL 对比图的可见文字统一使用 `with EDL` / `w/o EDL`；内部变量、CSV 字段和文件名里的 `no_edl` / `without_edl` 为追溯稳定性保留不改。

## Mixed_Potential_Electrical_Double_Layer/ - 模型代码与结果

- 主线性求解文件是 `Solve_Emix_updating.py`。
- `Solve_Emix_nonlinearPB.py` 是 nonlinear PB 版本；之前 review 时用户明确说“不用看 nonlinear part”。
- 线性模型核心包括 Debye-Huckel/linearized PB, Stern/linear charging BC, Frumkin-corrected Butler-Volmer kinetics, and mixed-potential root solve。
- mixed potential 的根本判据是绝对电流平衡 `I_Au + I_Pd = 0`，不是分别按不同电极面积归一化后的 current density 相等。画 mixed-potential balance 图时优先用绝对电流；若使用 current density，必须明确是用同一个总 reactive area 做共同归一化，不能用 Au/Pd 各自面积归一化后找交点。
- 之前 review 的结论：主线性方程符号大体自洽；闭式解和 root solve 在默认参数下能对到机器精度；均一边界条件会退化到解析常数解。
- 重要 caveat：默认参数下 Debye-Huckel 适用性可能超限，self-check 曾给 `max |phi_tilde| = 5.4068`，高于默认阈值 1。
- `compare_figure_parameters_and_methods.md` 的 baseline 已改为 `Figures/Figure_same_length_i0_alpha` 使用的参数，而不是原始 `results/20260528_111255/params.json` baseline：
  - 参数来源：`../Figures/Figure_same_length_i0_alpha/inputs/params_same_length_i0_alpha050_au25_pd25_20260528_111255.json`。
  - summary 来源：`../Figures/Figure_same_length_i0_alpha/inputs/summary_compare_same_length_i0_alpha050_au25_pd25_20260528_111255.csv`。
  - baseline 为 `L_Au/L_gap/L_Pd_len = 25/10/25 nm`、`it0_1=it0_2=1.852573885166257e-4 A/m^2`、`alpha1=alpha2=0.5`、`out_of_plane_width=0.01 m`。
  - 文档中的 caveat 使用 same_length_i0_alpha 的 `max_abs_phi_tilde = 6.038944611092431 > 1`。

## Mixed_Potential_Electrical_Double_Layer/Solve_Emix_updating.py - 已修复事项

- 已修复 optional overrides 的 finite 检查：
  - `epsilon_s` 必须 finite 且 `> 0`。
  - `lambda_D` 必须 finite 且 `> 0`。
  - `g_Au/g_C/g_Pd` 必须 finite 且 `>= 0`。
- 该修复已验证：
  - 默认参数仍能通过 `validate_params()` 和 `compute_derived_params()`。
  - `lambda_D/epsilon_s/g_* = nan/inf/-inf` 会抛 `ValueError`。
  - `python3 -m py_compile Mixed_Potential_Electrical_Double_Layer/Solve_Emix_updating.py` 通过。
- 已更新线性 solver 的 with/w/o EDL 对比配色，使其与 `Figures/Figure_3/` 保持一致：
  - `with EDL`：亮暖色 `#F26B38`，辅助暖色 `#D83A2E` / `#F2B134`。
  - `w/o EDL`：暗冷色 `#12355B`，辅助冷色 `#2D5A7B`。
  - 适用于 compare 图、publication compare panels、OFAT 对比图；heatmap 连续 colormap 保持不变。

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
- 该目录下 PNG 图已按 Figure 3 逻辑重画配色：
  - `with EDL` 为亮橙红。
  - `w/o EDL` 为深蓝。
  - 已重画 baseline profiles、main/with_edl/no_edl compare 图和 66 个 OFAT PNG；heatmap PNG 未改连续 colormap。
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
  - `E_mix w/o EDL = 0.49 V`
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
- EDL vs w/o EDL BV 对比图脚本：`Figures/make_edl_vs_no_edl_bv_mixed_potential.py`。
  - `use_edl=True` 曲线用实线；`use_edl=False` 曲线用虚线。
  - 标出 `E_mix with EDL = 0.63 V` 和 `E_mix w/o EDL = 0.49 V`，并标出对应 `|i|`。
  - 当前版本按用户要求改成 Nature-style/clean paper figure 风格。
  - 字体栈为 `Helvetica, Nimbus Sans, Arial, DejaVu Sans, sans-serif`；本机没有真正 Helvetica，PNG 实际用 Helvetica-compatible `Nimbus Sans`，SVG 普通文字保留 Helvetica-first 字体栈且 `svg.fonttype="none"`。
  - 导出：
    - `Figures/edl_vs_no_edl_bv_mixed_potential_20260528_111255.png`
    - `Figures/edl_vs_no_edl_bv_mixed_potential_20260528_111255.svg`
- 带 PZC 的 EDL vs w/o EDL BV 对比图脚本：`Figures/make_edl_vs_no_edl_bv_mixed_potential_with_pzc.py`。
  - 在 Nature-style EDL/w/o EDL 对比图基础上增加 PZC lane。
  - PZC 标注为 `PZC support = 0.50 V`、`PZC Pd = 0.78 V`、`PZC Au = 0.93 V`。
  - 为显示 `PZC Au = 0.93 V`，横轴右端扩到约 `0.97 V`。
  - 主图中用淡金色竖虚线对齐 PZC 位置，下方用三角 marker 和文字标注 PZC。
  - 导出：
    - `Figures/edl_vs_no_edl_bv_mixed_potential_with_pzc_20260528_111255.png`
    - `Figures/edl_vs_no_edl_bv_mixed_potential_with_pzc_20260528_111255.svg`
- 用户明确要求不再生成 PDF；不要重新加入 PDF 输出。
- 不要碰 `Figures/Figure_1_v2.ai`，除非用户明确要求。

## Figures/Figure_phi_RP_CH_cion/ - 单一均一晶面下 C_H/c_ion 对 phi_RP 的解释图

- 该目录用于解释 homogeneous single-surface 情况下 `E < PZC` 时 `C_H` 和 `c_ion` 如何影响 reaction-plane potential `phi_RP`。
- 当前脚本是 `Figures/Figure_phi_RP_CH_cion/make_phi_rp_ch_cion_explanation.py`。
- 示例条件：
  - `E = 0.40 V`
  - `PZC = 0.60 V`
  - homogeneous surface: `Cdl_Au = Cdl_C = Cdl_Pd = C_H` 且 `pzc_Au = pzc_C = pzc_Pd = PZC`
  - `C_H` 扫描固定 `c_ion = 0.01 M`
  - `c_ion` 扫描固定 `C_H = 0.20 F/m^2`
- 关键解析关系：
  - `phi_RP = [g / (1 + g)] * (E - PZC)`
  - `g = lambda_D * C_H / epsilon_s = C_H / C_D`
- 关键结论：
  - 当 `E < PZC` 时，提高 `C_H` 会使 `phi_RP` 更负。
  - 固定 `C_H` 时，提高 `c_ion` 会缩短 `lambda_D`、增大 diffuse capacitance，使 `phi_RP` 向 0 正移。
- 只导出 PNG/SVG，不导出 PDF：
  - `phi_rp_CH_sweep_homogeneous_E040_PZC060.png/svg`
  - `phi_rp_cion_sweep_homogeneous_E040_PZC060.png/svg`
  - `phi_rp_CH_cion_heatmap_homogeneous_E040_PZC060.png/svg`
  - `phi_rp_CH_cion_explanation_homogeneous_E040_PZC060.png/svg`
- 支撑数据：
  - `Figures/Figure_phi_RP_CH_cion/inputs/inputs_homogeneous_E040_PZC060.json`
  - `Figures/Figure_phi_RP_CH_cion/csv/phi_rp_CH_sweep_homogeneous_E040_PZC060.csv`
  - `Figures/Figure_phi_RP_CH_cion/csv/phi_rp_cion_sweep_homogeneous_E040_PZC060.csv`
  - `Figures/Figure_phi_RP_CH_cion/csv/phi_rp_CH_cion_heatmap_homogeneous_E040_PZC060.csv`

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
  - `w/o EDL` 用暗冷色/navy-blue family。
  - panel c 保持 log y-scale。
  - panel b legend 放在 `center right` 且 `bbox_to_anchor=(0.98, 0.50)`，避免与曲线重合。
  - panel f 是 PZC + potential reference map，不是 BV+PZC current plot。
  - panel f 不显示左侧 lane 标签 `Equilibrium potentials` / `Mixed potential` / `PZC`；PZC support 灰色 `#8C8C8C`，PZC Pd 蓝色 `#5A90C8`，PZC Au 金色 `#E4C133`。
  - panel f 横轴标签为 `Potential (V vs. RHE)`。
  - 图片内部已按用户要求删除 panel 字母；文件名仍保留 `panel_a` 等用于追溯，不代表图片里有字母。
- 脚本有 same-series 可配置 hook：
  - `PANEL_D_TITLE` / `PANEL_E_TITLE` 用于 wrapper 覆盖 panel d/e 标题。
  - `PANEL_E_YMIN` 用于 wrapper 固定 panel e 的 y 轴下界。
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
- `make_phi_s_reactants_2d.py` 已兼容 `support=0 nm` 的零宽 support：材料 lane 会跳过零宽 support 标签，区域边界会去重。

## Figures/Figrue_RP/Figure_same_length_i0_alpha/ - 等长等 i0 等 alpha 的 RP 2D 汇总

- 当前脚本是 `Figures/Figrue_RP/Figure_same_length_i0_alpha/make_phi_s_reactants_2d_same_length_i0_alpha_collection.py`。
- 脚本复用：
  - `Figures/Figure_same_length_i0_alpha/same_length_i0_alpha_common.py`
  - `Figures/Figrue_RP/make_phi_s_reactants_2d.py`
- 该目录集中保存 `Figure_same_length_i0_alpha/Figrue_RP` 条件的 RP 2D 图，并额外生成 `support=0 nm` 版本。
- baseline same_length_i0_alpha 条件：
  - `L_Au / L_gap / L_Pd_len = 25 / 10 / 25 nm`
  - 输出 tag：`same_length_i0_alpha050_au25_pd25_20260528_111255`
  - `E_mix_with = 0.5979829354430014 V`
  - `i_mix_avg_with = 0.08384634584416407 A/m^2`
  - 输出：
    - `Figures/Figrue_RP/Figure_same_length_i0_alpha/phi_s_reactants_2d_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
- support=0 nm 条件：
  - `L_Au / L_gap / L_Pd_len = 25 / 0 / 25 nm`
  - 其他参数保持 same_length_i0_alpha，包括等 i0、`alpha1 = alpha2 = 0.5`、PZC、Cdl、charges、pH。
  - 输出 tag：`same_length_i0_alpha050_au25_pd25_support0_20260528_111255`
  - `E_mix_with = 0.600693745661775 V`
  - `E_mix_no = 0.4670000000000001 V`
  - `i_mix_avg_with = 0.08160442531462271 A/m^2`
  - `i_mix_avg_no = 0.11756035407872442 A/m^2`
  - `i_mix_abs_with = 4.080221265731136e-11 A`
  - `i_mix_abs_no = 5.878017703936221e-11 A`
  - `max |phi_tilde| = 5.985937034969025`
  - 输出：
    - `Figures/Figrue_RP/Figure_same_length_i0_alpha/phi_s_reactants_2d_same_length_i0_alpha050_au25_pd25_support0_20260528_111255.png/svg`
- support 长度影响结论：在该 same_length_i0_alpha 条件下，从 `L_gap = 10 nm` 改成 `0 nm` 对结果影响很小：
  - `E_mix_with` 从 `0.5979829354 V` 到 `0.6006937457 V`，约 `+2.71 mV`。
  - `i_mix_avg_with` 从 `0.0838463458` 到 `0.0816044253 A/m^2`，约 `-2.7%`。
  - 远小于 EDL 本身造成的 `E_mix` shift（约 `0.131-0.134 V`）。
- 该目录的 `inputs/` 保存两组图对应的 `params_*.json`、`overrides_*.json`、`summary_compare_*.csv/json`，用于追溯参数。
- 已验证：脚本运行成功，输出 2 PNG + 2 SVG + 0 PDF；support=0 图中底部材料 lane 只显示 Au/Pd，中间 25 nm 处相接。

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
- 只导出 PNG/SVG，不导出 PDF；`Figure_scheme` 只生成带 PZC 的 EDL vs w/o EDL BV 图。
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
- 只导出 PNG/SVG，不导出 PDF；`Figure_scheme` 只生成带 PZC 的 EDL vs w/o EDL BV 图。
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
- 只导出 PNG/SVG，不导出 PDF；`Figure_scheme` 原有带 PZC 的 EDL vs w/o EDL BV 图，另有解释性 schematic PNG。
- `Figure_3/` 当前图件细节：
  - `figure_3_panel_b_reaction_plane_potential_*` 的 legend 已统一下移到图框右侧中线，避免与曲线重合。
  - `figure_3_panel_c_local_reactant_concentration_*` 标题为 `Local reactant concentration at RP`。
  - `figure_3_panel_d_local_overpotential_*` 标题为 `Local overpotential at RP`。
  - `figure_3_panel_e_local_current_density_*` 标题为 `Local current density at RP`，y 轴下界固定为 `-400`。
  - `figure_3_panel_f_pzc_potential_reference_map_*` 去掉左侧 `Equilibrium potentials` / `Mixed potential` / `PZC` lane 标签；PZC Pd 蓝色 `#5A90C8`，PZC Au 金色 `#E4C133`；横轴为 `Potential (V vs. RHE)`。
- `Figure_scheme/edl_vs_no_edl_bv_mixed_potential_with_pzc_*` 横轴为 `Potential (V vs. RHE)`；`PZC Pd` 和 `PZC Au` 颜色规则跟 Figure 3 panel f 保持一致时优先复用同一色系。
- EDL 使 `E_mix` 上升但 `i_mix` 下降的解释性 schematic：
  - 脚本：`Figures/Figure_same_length_i0_alpha/Figure_scheme/make_emix_up_imix_down_schematic_same_length_i0_alpha.py`
  - 输出：`Figures/Figure_same_length_i0_alpha/Figure_scheme/emix_up_imix_down_schematic_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
  - 输出 PNG/SVG，不输出 PDF。
  - 当前版本只保留单 panel，没有左上角 `a` panel 标题。
  - 横轴标签为 `Potential (V vs. RHE)`。
  - 图例文字为 `Oxidation on Au, with EDL`、`Reduction on Pd, with EDL`、`Oxidation on Au, w/o EDL`、`Reduction on Pd, w/o EDL`。
  - 图中用单向箭头标注 `E_mix` 从 `0.47 V` 上移到 `0.60 V`；纵轴为 `60 nm` 周期单元的绝对电流，单位写作 `Current (10^-3 uA)`，单位正体且与横轴统一使用括号；并用 `$I_{\mathrm{mix}}$ drops` 标注 `|I|` 从 `0.059 x 10^-3 uA` 降到 `0.042 x 10^-3 uA`。
- 用真实 half-reaction 曲线确定 `E_mix` 和 `I_mix` shift 的 schematic：
  - 脚本：`Figures/Figure_same_length_i0_alpha/Figure_scheme/make_half_reaction_shift_schematic_same_length_i0_alpha.py`
  - 输出：`Figures/Figure_same_length_i0_alpha/Figure_scheme/half_reaction_shift_schematic_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
  - 输出 PNG/SVG，不输出 PDF。
  - 左侧画真实模型的 `I_Au(E)` 与 `|I_Pd(E)|` half-reaction magnitude 曲线，y 轴为 log scale，交点即 `I_Au + I_Pd = 0` 的 mixed-potential balance。
  - 图中显示 w/o EDL 交点在 `E_mix = 0.467 V`、`I_mix = 0.0588 x 10^-3 uA`；在同一旧电位打开 EDL 后 `I_Au = 0.00102 x 10^-3 uA`、`|I_Pd| = 2.695 x 10^-3 uA`，出现 cathodic imbalance；因此电位正移到 with-EDL 新交点 `E_mix = 0.598 V`、`I_mix = 0.0419 x 10^-3 uA`。
- `C_tot` 高盐回落机制 schematic：
  - 脚本：`Figures/Figure_same_length_i0_alpha/Figure_scheme/make_ctot_high_salt_regime_schematic_same_length_i0_alpha.py`
  - 输出：`Figures/Figure_same_length_i0_alpha/Figure_scheme/ctot_high_salt_regime_schematic_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
  - 输出 PNG/SVG，不输出 PDF。
  - 用 `0.01 M`、`1 M`、`10^3 M` 三个代表点解释：低盐时 EDL 直接抑制 Au 占主导；中间盐度时 `E_mix` 正移占主导并使 with-EDL `I_mix` overshoot；formal high-salt endpoint 时 EDL 项衰减，with EDL 从上方回到 w/o EDL。
  - 纵轴为 `60 nm` 周期单元的绝对电流，单位写作 `Current (10^-3 uA)`；`10^3 M` 仅用于展示数学高盐极限趋势，不表示物理可实现浓度。
- `C_tot` 三阶段 half-reaction polarization overlay schematic：
  - 脚本：`Figures/Figure_same_length_i0_alpha/Figure_scheme/make_ctot_half_reaction_polarization_overlay_same_length_i0_alpha.py`
  - 输出：`Figures/Figure_same_length_i0_alpha/Figure_scheme/ctot_half_reaction_polarization_overlay_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
  - 输出 PNG/SVG，不输出 PDF。
  - 单图叠加 `0.01 M`、`1 M`、`10^3 M` 的 with-EDL signed polarization curves：Au oxidation 为正电流，Pd reduction 为负电流；并用一组 w/o EDL reference curves 对照。每个 `E_mix` 处上下 half-reaction 电流等大反号，即 `I_Au + I_Pd = 0` 的 mixed-potential balance。
  - 该图用于解释三阶段：`0.01 M` 时 EDL 直接抑制 Au，`I_with/I_no = 0.713`；`1 M` 时 `E_mix` 正移主导，`I_with/I_no = 1.069`；`10^3 M` 时 EDL 项衰减，`I_with/I_no = 1.004`，回到 w/o EDL。
- 关键结果：
  - `E_mix_with = 0.5979829354430014 V`
  - `E_mix_no = 0.4670000000000001 V`
  - `i_mix_avg_with = 0.08384634584416407 A/m^2`
  - `i_mix_avg_no = 0.11756035407872442 A/m^2`
  - `i_mix_abs_with = 4.192317292208204e-11 A`
  - `i_mix_abs_no = 5.878017703936221e-11 A`
  - `lambda_D = 3.041217889 nm`
  - `max |phi_tilde| = 6.038944611092431`
- 该条件下即使 `L/i0/alpha` 都相同，with EDL 和 w/o EDL 的 `E_mix` 仍相差约 `0.131 V`。原因不是几何或 i0，而是 EDL 改变了 reaction-plane potential 和局部反应物浓度：BV 局部过电位含 `E_mix - E_eq - phi_RP(x)`，浓度含 `exp(-z_i * phi_tilde)`，因此 Frumkin/Boltzmann 权重会强烈改变 Au/Pd 两个 half-reaction 的相对强度。

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

## Figures/Figure_scan/ - 等长等 i0 等 alpha baseline 的完整扫描图

- 当前脚本是 `Figures/Figure_scan/make_scan_figures_same_length_i0_alpha.py`。
- baseline 使用 `Figures/Figure_same_length_i0_alpha/same_length_i0_alpha_common.py`：
  - `L_Au / L_gap / L_Pd_len = 25 / 10 / 25 nm`
  - `it0_1 = it0_2 = 1.852573885166257e-4 A/m^2`
  - `alpha1 = alpha2 = 0.5`
  - 输出 tag：`same_length_i0_alpha050_au25_pd25_20260528_111255`
- 参考 `Mixed_Potential_Electrical_Double_Layer/results/20260528_111255/figures/` 的扫描图生成逻辑，只保留 PNG，不生成 SVG/PDF。
- 扫描图样式已在 wrapper 内局部覆盖，不改 solver 默认全局行为：
  - `i_mix_avg` 的显示 label 改为 `Mixed current density, \bar{i}_{mix} (A/m^2)`，去掉 `Average`；CSV 字段名和计算仍保持 `i_mix_avg`。
  - 字体栈改为 `Helvetica, Nimbus Sans, Arial, DejaVu Sans, sans-serif`，mathtext 使用 Nimbus Sans，和 `Figure_same_length_i0_alpha/Figure_3` 保持一致。
  - OFAT 单图字号放大，并通过 wrapper 的本地 `finalize_scan_figure(...)` 增大 tight-bbox padding，避免 y 轴标签贴边。
  - `C_tot` OFAT 在 wrapper 内局部扩展到 `10^3 M`，并单独使用 25 个 log-spaced 点；这是 formal high-salt extension，用于展示 with EDL 的 `i_mix` 先超过 w/o EDL、再从上方回落到 w/o EDL。
- 图件输出在 `Figures/Figure_scan/figures/`：
  - 66 个 OFAT PNG：22 个参数，每个参数包含 `E_mix`、`i_mix_avg_A_per_m2` 和 combined 三张图。
  - 2 个 combined heatmap PNG：`heatmap_combined_panel_log.png` 和 `heatmap_combined_panel_linear.png`。
  - 已验证输出为 68 PNG + 0 SVG + 0 PDF。
- 支撑数据：
  - `Figures/Figure_scan/params.json`
  - `Figures/Figure_scan/inputs/params_same_length_i0_alpha050_au25_pd25_20260528_111255.json`
  - `Figures/Figure_scan/inputs/overrides_same_length_i0_alpha050_au25_pd25_20260528_111255.json`
  - `Figures/Figure_scan/inputs/summary_compare_same_length_i0_alpha050_au25_pd25_20260528_111255.csv/json`
  - `Figures/Figure_scan/csv/` 保存 OFAT CSV、log/linear heatmap CSV、`summary_compare.csv/json` 和 `results_summary.csv`。
- 关键 baseline 数值：
  - `E_mix_with = 0.5979829354430014 V`
  - `E_mix_no = 0.4670000000000001 V`
  - `i_mix_avg_with = 0.08384634584416407 A/m^2`
  - `i_mix_avg_no = 0.11756035407872442 A/m^2`

## Figures/Figrue_4/ - C_tot 变化机制图

- 当前脚本是 `Figures/Figrue_4/make_ctot_study_figures.py`。
- 使用 `Figures/Figure_same_length_i0_alpha/same_length_i0_alpha_common.py` 的 baseline：
  - `L_Au / L_gap / L_Pd_len = 25 / 10 / 25 nm`
  - `it0_1 = it0_2 = 1.852573885166257e-4 A/m^2`
  - `alpha1 = alpha2 = 0.5`
  - 输出 tag：`same_length_i0_alpha050_au25_pd25_20260528_111255`
- 输出 3 组 PNG/SVG，不输出 PDF：
  - `ctot_emix_high_salt_regime_schematic_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
  - `ctot_high_salt_regime_schematic_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
  - `ctot_half_reaction_polarization_overlay_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
- 新图比 `Figure_same_length_i0_alpha/Figure_scheme/` 参考图减少图内说明文字，保留曲线、坐标轴、legend、代表点和背景分区。
- `10 M` 已显式加入 `C_tot` 扫描网格；两张趋势图中 `10 M -> 10^3 M` 的理论高盐推演线段用同色浅透明线表示。
- 两张趋势图 `ctot_emix_high_salt_regime_schematic_*` 和 `ctot_high_salt_regime_schematic_*` 使用窄版尺寸 `TREND_FIGSIZE = (4.15, 3.45)`；`ctot_half_reaction_polarization_overlay_*` 保持 `POLARIZATION_FIGSIZE = (7.2, 4.35)`。
- 如果以后需要微调 Figure 4 的宽度，改 `Figures/Figrue_4/make_ctot_study_figures.py` 里的 `TREND_FIGSIZE` 并重导出 PNG/SVG，不直接改导出的 SVG。
- 支撑数据：
  - `Figures/Figrue_4/csv/ctot_scan_same_length_i0_alpha050_au25_pd25_20260528_111255.csv`
  - `Figures/Figrue_4/inputs/params_*.json`、`overrides_*.json`、`summary_compare_*.csv/json`

## Figures/Figure_5/ - C_H heatmap/mechanism 图件

- 用户要求把 `Figures/Figure_4/` 改成 `Figures/Figure_5/`，并连带目录下图片改名。
- Figure 5 可见命名约定：图面和新输出文件名使用 `C_H` / `ch`；内部模型参数、CSV 字段、旧输入键仍使用 `Cdl_Au`、`Cdl_C`、`Cdl_Pd` 以保持 solver 和历史数据兼容。
- 目录结构：
  - `Heatmap/`
  - `Mechanism/`
- `Heatmap/` 脚本是 `Figures/Figure_5/Heatmap/make_heatmap_combined_panel_log_same_length_i0_alpha.py`，从 `Figures/Figure_same_length_i0_alpha/same_length_i0_alpha_common.py` 读取 helper，并输出到当前 `Figure_5/Heatmap/`。
- `Heatmap/` 当前输出：
  - `Figures/Figure_5/Heatmap/heatmap_combined_panel_log.png`
  - `Figures/Figure_5/Heatmap/heatmap_combined_panel_log.svg`
  - `Figures/Figure_5/Heatmap/heatmap_combined_panel_log_3d_CH_pzc_length.png`
  - `Figures/Figure_5/Heatmap/heatmap_combined_panel_log_3d_CH_pzc_length.svg`
  - `csv/` 下 30 个 `heatmap_compare_*.csv`，仍保留内部 `Cdl*` CSV 轴字段名。
- Figure 5 heatmap 字号在 wrapper 内局部放大，不改 `Solve_Emix_updating.py` 的全局 heatmap 默认字号。
- Figure 5 heatmap 的电流 colorbar/label 显示为 `Mixed current density`，不写 `Average mixed current density`；CSV 和内部字段仍可保留 `i_mix_avg`。
- 3D heatmap surface 使用和 2D combined panel 相同的三组扫描与两个输出量：`pzc_Au × pzc_Pd`、`C_H,Au × C_H,Pd`、`L_Au × L_Pd`；`E_mix` 和 `i_mix`。
- `Mechanism/` 下脚本已从 `make_figure_4_process_gradients.py` 改为 `make_figure_5_process_gradients.py`。
- `Mechanism/` 下所有 `figure_4_*` 输出已改为 `figure_5_*`，并重新运行脚本使图内可见标题也从 Figure 4 改为 Figure 5。
- `Mechanism/` 机制链图已拆成单列 mechanism-only 图和 polarization-only 图；旧的 `figure_5_column_*` 组合图不再作为当前 Figure 5 deliverable。
- 机制链当前 7 个 panel 依次为：`sigma`、active-side 平均 `phi_RP`、active-side 平均 `c_Red_1/C_bulk` 或 `c_Ox_2/C_bulk`、active-side 平均 overpotential、BV exponential factor、`[C] × exp(overpotential)` 的无量纲 BV driving weight、mixed current。
- 机制图中 active-side 平均量用尖括号显示，不用 overbar；`sigma` 图面单位为 `μC/cm^2`。机制单列图字号已在脚本内放大。
- 机制图的浓度项不要显示泛称 `c_react`；Au 侧显示 `c_Red_1/c_bulk`，Pd 侧显示 `c_Ox_2/c_bulk`，`[C] × exp(overpotential)` panel 也跟随对应物种。
- `[C] × exp(overpotential)` 不是 current 本身；只有再乘以 `i0`、符号/计量因子并在反应区积分/归一化后才成为 half-reaction current 或 mixed current。
- `Figures/Figure_5/Mechanism/` 当前输出：
  - 1 个 overview：`figure_5_process_gradients_same_length_i0_alpha050_au25_pd25_20260528_111255.png/svg`
  - 4 个 mechanism-only 单列图：`figure_5_mechanism_ch_au_causal_chain_*`、`figure_5_mechanism_ch_pd_causal_chain_*`、`figure_5_mechanism_pzc_au_causal_chain_*`、`figure_5_mechanism_pzc_pd_causal_chain_*`
  - 4 个 polarization-only 图：`figure_5_polarization_ch_au_*`、`figure_5_polarization_ch_pd_*`、`figure_5_polarization_pzc_au_*`、`figure_5_polarization_pzc_pd_*`
  - `csv/` 下 3 个 `figure_5_*.csv`
- 已验证：`python3 -m py_compile` 通过；`Mechanism/` 输出为 9 PNG + 9 SVG + 0 PDF；`Heatmap/` 输出为 2 PNG + 2 SVG + 0 PDF；Figure 5 生成 SVG 中无旧电容显示记号或旧 EDL 对照标签。

## Git 状态记忆

- 曾经清理过工作树：
  - 内层 repo 提交：`6b892ea Record result parameters and tighten validation`
  - 外层 repo 提交：`6649f9f Update EDL results submodule`
- 后续新增了 `Figures/` 下的 BV/EDL 图脚本、Figure 3 独立 panel 脚本和导出图；如果用户要求“清理工作树”，需要考虑是否提交 `Figures/` 和更新后的 `AGENTS.md`。
- 当前未提交上下文包括本轮图件修订：
  - `AGENTS.md` 已更新本轮记忆。
  - `Mixed_Potential_Electrical_Double_Layer/compare_figure_parameters_and_methods.md` 已改为 same_length_i0_alpha baseline。
  - `Figures/Figure_3/make_figure_3_panels.py` 有 panel b legend、panel f PZC 颜色/标签、panel d/e title hook、panel e y-min hook、`Potential (V vs. RHE)` 等改动。
  - `Figures/Figure_same_length_i0_alpha/Figure_3/make_figure_3_panels_same_length_i0_alpha.py` 设定 panel c/d/e 标题和 panel e 下界。
  - `Figures/Figure_scan/make_scan_figures_same_length_i0_alpha.py` 设定扫描图字体、`Mixed current density` 显示 label、OFAT 导出 padding；`Figures/Figure_scan/figures/` 68 个 PNG 已重导出，无 SVG/PDF。
  - `Figures/Figure_scheme/make_edl_vs_no_edl_bv_mixed_potential_with_pzc.py` 和 `Figures/Figure_same_length_i0_alpha/Figure_scheme/make_emix_up_imix_down_schematic_same_length_i0_alpha.py` 已使用 `Potential (V vs. RHE)`。
- 不要使用 destructive git 命令；不要 revert 用户未要求还原的文件。
