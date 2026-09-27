q6_folder = fileparts(mfilename('fullpath'));
cd(q6_folder);
run(fullfile(q6_folder,'init_RRRP.m'));
q6_folder = fileparts(mfilename('fullpath')); 
cd(q6_folder);
model = 'untitled';
load_system(fullfile(q6_folder,'untitled.slx'));
scenarios = {
    'low_25pct',       .25, .25, .25, .25, .25, .25;
    'original',         1,    1,    1,    1,    1,    1;
    'tuned',            2,    1,    2.5,  1,    1,    1;
    'high_P_I',         4,    2,    1,    4,    2,    1;
    'high_with_D',      4,    2,    4,    4,    2,    4
};
baseP=[Kp1 Kp2 Kp3 Kp4];
baseI=[Ki1 Ki2 Ki3 Ki4];
baseD=[Kd1 Kd2 Kd3 Kd4];
actual_names={'q1_act','q2_act','q3_act','d4_act'};
desired_names={'q1_des','q2_des','q3_des','d4_des'};
unit={'deg','deg','deg','m'};
runs=cell(size(scenarios,1),1);
row=0;
records=struct('Scenario',{},'Joint',{},'Kp',{},'Ki',{},'Kd',{}, ...
    'RMSE',{},'PeakAbsErrorAfter025s',{},'FinalErrorAt12s',{},'Unit',{});

for s=1:size(scenarios,1)
    label=scenarios{s,1};
    in=Simulink.SimulationInput(model);
    in=in.setModelParameter('StopTime','12');
    for j=1:4
        if j<=3
            p=baseP(j)*scenarios{s,2};
            i=baseI(j)*scenarios{s,3};
            d=baseD(j)*scenarios{s,4};
            in=in.setVariable(sprintf('Kp%d',j),p/2);
            in=in.setVariable(sprintf('Ki%d',j),i);
            in=in.setVariable(sprintf('Kd%d',j),d/2.5);
        else
            p=baseP(j)*scenarios{s,5};
            i=baseI(j)*scenarios{s,6};
            d=baseD(j)*scenarios{s,7};
            in=in.setVariable('Kp4',p);
            in=in.setVariable('Ki4',i);
            in=in.setVariable('Kd4',d);
        end
        row=row+1;
        records(row).Scenario=label;
        records(row).Joint=j;
        records(row).Kp=p;
        records(row).Ki=i;
        records(row).Kd=d;
        records(row).Unit=unit{j};
    end
    fprintf('Running %s ...\n',label);
    runs{s}=sim(in);
    for j=1:4
        actual=runs{s}.get(actual_names{j});
        desired=runs{s}.get(desired_names{j});
        [td,first]=unique(desired.Time,'stable');
        yd=squeeze(desired.Data); yd=yd(first);
        ta=actual.Time; ya=squeeze(actual.Data);
        if j<=3, yd=rad2deg(yd); ya=rad2deg(ya); end
        e=ya-interp1(td,yd,ta,'linear','extrap');
        idx=(s-1)*4+j;
        records(idx).RMSE=sqrt(trapz(ta,e.^2)/(ta(end)-ta(1)));
        records(idx).PeakAbsErrorAfter025s=max(abs(e(ta>=.25)));
        records(idx).FinalErrorAt12s=e(end);
    end
end

tbl=struct2table(records);
writetable(tbl,fullfile(q6_folder,'Q6_debug_record.csv'));
save(fullfile(q6_folder,'Q6_debug_runs.mat'),'runs','scenarios','tbl','-v7.3');
disp(tbl);

fig=figure('Name','RRRP PID gain comparison','Color','w');
tiledlayout(2,2,'TileSpacing','compact','Padding','compact');
for j=1:4
    nexttile; hold on; grid on;
    d=runs{2}.get(desired_names{j}); yd=squeeze(d.Data);
    if j<=3, yd=rad2deg(yd); end
    plot(d.Time,yd,'k','LineWidth',1.8,'DisplayName','desired');
    for s=1:size(scenarios,1)
        a=runs{s}.get(actual_names{j}); ya=squeeze(a.Data);
        if j<=3, ya=rad2deg(ya); end
        plot(a.Time,ya,'LineWidth',1.1,'DisplayName',scenarios{s,1});
    end
    xlabel('Time (s)'); ylabel(unit{j}); title(actual_names{j});
end
legend('Location','bestoutside');
exportgraphics(fig,fullfile(q6_folder,'Q6_debug_comparison.png'),'Resolution',180);
