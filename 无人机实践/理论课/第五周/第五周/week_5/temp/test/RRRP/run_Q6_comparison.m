%% Question 6: reproducible RRRP PID gain comparison.
% Requires Simscape and Simscape Multibody installed and licensed.
% Run this script from any folder. It leaves the instructor's files intact.
rrrp_dir = fileparts(mfilename('fullpath'));
cd(rrrp_dir);
run(fullfile(rrrp_dir,'init_RRRP.m'));
rrrp_dir = fileparts(mfilename('fullpath')); % init_RRRP calls clear.
Tsim = 8; % Last commanded motion ends at 5 s; retain 3 s to assess settling.
model = 'RRRP_PID_Control';
load_system(model);

names = {'baseline','all_25_percent','R1_25_percent','R2_25_percent', ...
    'R3_25_percent','P4_25_percent'};
scale = [ones(1,4); .25*ones(1,4); ...
    .25 1 1 1; 1 .25 1 1; 1 1 .25 1; 1 1 1 .25];
kp = [Kp1 Kp2 Kp3 Kp4];
ki = [Ki1 Ki2 Ki3 Ki4];
kd = [Kd1 Kd2 Kd3 Kd4];

results = struct;
for trial = 1:numel(names)
    in = Simulink.SimulationInput(model);
    in = in.setModelParameter('StopTime','8');
    for j = 1:4
        in = in.setVariable(sprintf('Kp%d',j),kp(j)*scale(trial,j));
        in = in.setVariable(sprintf('Ki%d',j),ki(j)*scale(trial,j));
        in = in.setVariable(sprintf('Kd%d',j),kd(j)*scale(trial,j));
    end
    fprintf('Running %s ...\n', names{trial});
    out = sim(in);
    results.(names{trial}) = out;
end

fig = figure('Name','Q6 RRRP gain comparison','Color','w');
tiledlayout(2,2,'TileSpacing','compact');
labels = {'R1 (deg)','R2 (deg)','R3 (deg)','P4 (m)'};
score = zeros(numel(names),4);
for j=1:4
    dname = {'q1_des','q2_des','q3_des','d4_des'};
    aname = {'q1_act','q2_act','q3_act','d4_act'};
    nexttile; hold on; grid on;
    desired = results.baseline.get(dname{j});
    td = desired.Time; yd = squeeze(desired.Data);
    if j<4, yd = rad2deg(yd); end
    plot(td,yd,'k','LineWidth',1.8,'DisplayName','desired');
    for trial=1:numel(names)
        actual = results.(names{trial}).get(aname{j});
        ta = actual.Time; ya = squeeze(actual.Data);
        if j<4, ya = rad2deg(ya); end
        plot(ta,ya,'LineWidth',1.1,'DisplayName',names{trial});
        [td_unique,first] = unique(td,'stable');
        yd_at_actual = interp1(td_unique,yd(first),ta,'linear','extrap');
        score(trial,j)=sqrt(trapz(ta,(ya-yd_at_actual).^2)/(ta(end)-ta(1)));
    end
    xlabel('Time (s)'); ylabel(labels{j}); title(labels{j});
end
legend('Location','bestoutside');
exportgraphics(fig,fullfile(rrrp_dir,'Q6_gain_comparison.png'),'Resolution',180);
rows = array2table(score,'VariableNames',{'R1_RMSE_deg','R2_RMSE_deg','R3_RMSE_deg','P4_RMSE_m'});
rows.Case = string(names(:));
rows = movevars(rows,'Case','Before',1);
disp(rows);
writetable(rows,fullfile(rrrp_dir,'Q6_metrics.csv'));
save(fullfile(rrrp_dir,'Q6_comparison_data.mat'),'results','names','scale','score','-v7.3');
