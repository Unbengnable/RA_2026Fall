%% Start the completed RRRP Question 6 model from MATLAB.
% Run this script in the MATLAB Editor or enter start_Q6_tuned in Command Window.
rrrp_folder = fileparts(mfilename('fullpath'));
cd(rrrp_folder);
run(fullfile(rrrp_folder,'init_RRRP.m')); % Defines geometry, trajectory and PID variables.
rrrp_folder = fileparts(mfilename('fullpath')); % init_RRRP clears the workspace.
cd(rrrp_folder);
open_system(fullfile(rrrp_folder,'RRRP_Q6_Tuned.slx'));
set_param('RRRP_Q6_Tuned','SimulationCommand','start');
