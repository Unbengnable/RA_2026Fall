%% RRRP Joint Trajectory Tracking
% Desired trajectory vs Actual trajectory

figure('Units','normalized','OuterPosition',[0.10 0.10 0.80 0.78]);

tiledlayout(2,2, ...
    'TileSpacing','compact', ...
    'Padding','compact');


%% ================= R1 =================
nexttile;

q1d = rad2deg(squeeze(q1_des.Data));
q1  = rad2deg(squeeze(q1_act.Data));

plot(q1_des.Time, q1d, ...
    'LineWidth',1.8);

hold on;

plot(q1_act.Time, q1, ...
    '--', ...
    'LineWidth',1.8);

grid on;

xlabel('Time (s)');
ylabel('Joint Angle (deg)');
title('R1 Trajectory Tracking');

legend('Desired','Actual', ...
    'Location','best');


%% ================= R2 =================
nexttile;

q2d = rad2deg(squeeze(q2_des.Data));
q2  = rad2deg(squeeze(q2_act.Data));

plot(q2_des.Time, q2d, ...
    'LineWidth',1.8);

hold on;

plot(q2_act.Time, q2, ...
    '--', ...
    'LineWidth',1.8);

grid on;

xlabel('Time (s)');
ylabel('Joint Angle (deg)');
title('R2 Trajectory Tracking');

legend('Desired','Actual', ...
    'Location','best');


%% ================= R3 =================
nexttile;

q3d = rad2deg(squeeze(q3_des.Data));
q3  = rad2deg(squeeze(q3_act.Data));

plot(q3_des.Time, q3d, ...
    'LineWidth',1.8);

hold on;

plot(q3_act.Time, q3, ...
    '--', ...
    'LineWidth',1.8);

grid on;

xlabel('Time (s)');
ylabel('Joint Angle (deg)');
title('R3 Trajectory Tracking');

legend('Desired','Actual', ...
    'Location','best');


%% ================= P4 =================
nexttile;

d4d = squeeze(d4_des.Data);
d4  = squeeze(d4_act.Data);

plot(d4_des.Time, d4d, ...
    'LineWidth',1.8);

hold on;

plot(d4_act.Time, d4, ...
    '--', ...
    'LineWidth',1.8);

grid on;

xlabel('Time (s)');
ylabel('Displacement (m)');
title('P4 Trajectory Tracking');

legend('Desired','Actual', ...
    'Location','best');


%% ================= Overall =================
sgtitle('RRRP Joint Trajectory Tracking','FontSize',15,'FontWeight','bold');

% 统一放大坐标轴、标题和图例字体，便于展示
axs = findall(gcf,'Type','axes');
set(axs,'FontSize',11);

lgd = findall(gcf,'Type','legend');
set(lgd,'FontSize',10);