function make_Q6_low_gain
% Create a separate model for the low-gain experiment. Does not change source.
root=fileparts(mfilename('fullpath'));
warning('off','all');
load_system(fullfile(root,'RRRP_PID_Control.slx'));
target=fullfile(root,'RRRP_Q6_LowGain.slx');
save_system('RRRP_PID_Control',target);
[~,name]=fileparts(target);
for j=1:4
    b=sprintf('%s/PID_%s',name,choose_name(j));
    set_param(b,'P',sprintf('0.25*Kp%d',j), ...
        'I',sprintf('0.25*Ki%d',j), ...
        'D',sprintf('0.25*Kd%d',j));
end
set_param(name,'Description', ...
    'Q6 low-gain experiment: all PID gains are 25 percent of init_RRRP.m defaults. Run init_RRRP before simulation.');
save_system(name);
close_system(name,0);
fprintf('Created %s\n',target);
end
function n=choose_name(j)
if j<4, n=sprintf('R%d',j); else, n='P4'; end
end
