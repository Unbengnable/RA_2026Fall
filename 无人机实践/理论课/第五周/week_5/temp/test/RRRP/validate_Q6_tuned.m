%% Validate the saved tuned model over the original 60 s horizon.
root=fileparts(mfilename('fullpath')); cd(root);
run(fullfile(root,'init_RRRP.m'));
root=fileparts(mfilename('fullpath'));
model='RRRP_Q6_Tuned';
load_system(model);
out=sim(model,'StopTime','60');
dnames={'q1_des','q2_des','q3_des','d4_des'};
anames={'q1_act','q2_act','q3_act','d4_act'};
fid=fopen(fullfile(root,'Q6_validation_60s.txt'),'w');
for j=1:4
    d=out.get(dnames{j}); a=out.get(anames{j});
    [td,ix]=unique(d.Time,'stable'); yd=squeeze(d.Data); yd=yd(ix);
    e=squeeze(a.Data)-interp1(td,yd,a.Time,'linear','extrap');
    if j<4, e=rad2deg(e); unit='deg'; else, unit='m'; end
    assert(all(isfinite(e)),'Nonfinite joint error');
    fprintf(fid,'%s: final error %.6g %s, max abs error after 10 s %.6g %s\n', ...
        anames{j},e(end),unit,max(abs(e(a.Time>=10))),unit);
end
fclose(fid);
disp(fileread(fullfile(root,'Q6_validation_60s.txt')));
