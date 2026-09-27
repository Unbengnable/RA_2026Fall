function make_Q6_tuned
% Save empirically selected gains in an independent submission model.
root=fileparts(mfilename('fullpath'));
warning('off','all');
load_system(fullfile(root,'RRRP_PID_Control.slx'));
target=fullfile(root,'RRRP_Q6_Tuned.slx');
save_system('RRRP_PID_Control',target);
[~,name]=fileparts(target);
for j=1:3
    b=sprintf('%s/PID_R%d',name,j);
    set_param(b,'P',sprintf('2*Kp%d',j), ...
        'I',sprintf('Ki%d',j), ...
        'D',sprintf('2.5*Kd%d',j));
end
% P4 keeps the original PD gains and gravity compensation.
set_param(name,'Description', ...
    ['Q6 tuned controller. R1-R3: P=2x, D=2.5x, I=1x relative to ', ...
    'init_RRRP.m. P4 unchanged. Evaluated on the provided trajectory.']);
save_system(name);
close_system(name,0);
fprintf('Created %s\n',target);
end
