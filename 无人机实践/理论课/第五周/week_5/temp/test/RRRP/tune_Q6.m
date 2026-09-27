%% Empirical controller search around the instructor's RRRP gains.
rrrp_dir=fileparts(mfilename('fullpath'));
cd(rrrp_dir);
run(fullfile(rrrp_dir,'init_RRRP.m'));
rrrp_dir=fileparts(mfilename('fullpath'));
model='RRRP_PID_Control';
load_system(model);
kp=[Kp1 Kp2 Kp3 Kp4]; ki=[Ki1 Ki2 Ki3 Ki4]; kd=[Kd1 Kd2 Kd3 Kd4];
% [R1-R3 proportional scale, R1-R3 derivative scale, R1-R3 integral scale]
candidates=[1 1 1; 1.5 1 1; 1 1.5 1; 1.5 1.5 1; ...
    2 1.5 1; 1.5 2 1; 2 2 1; 2 2.5 1; 1.5 2 .5];
dname={'q1_des','q2_des','q3_des','d4_des'};
aname={'q1_act','q2_act','q3_act','d4_act'};
rmse=zeros(size(candidates,1),4); peakerr=rmse; finisherr=rmse;
runs=cell(size(candidates,1),1);
for trial=1:size(candidates,1)
    pscale=[repmat(candidates(trial,1),1,3) 1];
    dscale=[repmat(candidates(trial,2),1,3) 1];
    iscale=[repmat(candidates(trial,3),1,3) 1];
    in=Simulink.SimulationInput(model);
    in=in.setModelParameter('StopTime','8');
    for j=1:4
        in=in.setVariable(sprintf('Kp%d',j),kp(j)*pscale(j));
        in=in.setVariable(sprintf('Ki%d',j),ki(j)*iscale(j));
        in=in.setVariable(sprintf('Kd%d',j),kd(j)*dscale(j));
    end
    fprintf('Candidate %d/%d: P=%.2g D=%.2g I=%.2g\n',trial,size(candidates,1),candidates(trial,:));
    runs{trial}=sim(in);
    for j=1:4
        des=runs{trial}.get(dname{j}); act=runs{trial}.get(aname{j});
        [td,first]=unique(des.Time,'stable'); yd=squeeze(des.Data); yd=yd(first);
        ta=act.Time; ya=squeeze(act.Data);
        if j<4, yd=rad2deg(yd); ya=rad2deg(ya); end
        e=ya-interp1(td,yd,ta,'linear','extrap');
        rmse(trial,j)=sqrt(trapz(ta,e.^2)/(ta(end)-ta(1)));
        peakerr(trial,j)=max(abs(e(ta>=.25)));
        finisherr(trial,j)=abs(e(end));
    end
end
% P4 is unchanged in this search; use its RMSE as a monitoring metric.
score=sum(rmse(:,1:3),2);
[~,best]=min(score);
tbl=array2table([candidates rmse peakerr finisherr score], ...
    'VariableNames',{'Pscale','Dscale','Iscale','R1_RMSE_deg','R2_RMSE_deg', ...
    'R3_RMSE_deg','P4_RMSE_m','R1_Peak_deg','R2_Peak_deg','R3_Peak_deg', ...
    'P4_Peak_m','R1_Final_deg','R2_Final_deg','R3_Final_deg','P4_Final_m','Score'});
disp(tbl);
fprintf('Best candidate = %d\n',best);
writetable(tbl,fullfile(rrrp_dir,'Q6_tuning_metrics.csv'));
save(fullfile(rrrp_dir,'Q6_tuning_data.mat'),'runs','candidates','rmse','peakerr','finisherr','best','-v7.3');
fig=figure('Name','RRRP baseline versus selected tuning','Color','w');
tiledlayout(2,2,'TileSpacing','compact');
for j=1:4
    nexttile; hold on; grid on;
    des=runs{1}.get(dname{j}); ydes=squeeze(des.Data);
    old=runs{1}.get(aname{j}); yold=squeeze(old.Data);
    new=runs{best}.get(aname{j}); ynew=squeeze(new.Data);
    if j<4, ydes=rad2deg(ydes); yold=rad2deg(yold); ynew=rad2deg(ynew); end
    plot(des.Time,ydes,'k','LineWidth',1.8,'DisplayName','desired');
    plot(old.Time,yold,'--','LineWidth',1.2,'DisplayName','baseline');
    plot(new.Time,ynew,'LineWidth',1.4,'DisplayName','tuned');
    xlabel('Time (s)'); ylabel(dname{j});
end
legend('Location','bestoutside');
exportgraphics(fig,fullfile(rrrp_dir,'Q6_tuned_vs_baseline.png'),'Resolution',180);
