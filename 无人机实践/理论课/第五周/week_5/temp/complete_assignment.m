function complete_assignment
% Reproducible solution to assignment_26_3.mlx (R2026a).
root = fileparts(mfilename('fullpath'));
out = fullfile(root,'assignment_solution');
if ~exist(out,'dir'), mkdir(out); end
cd(out);
set(0,'DefaultFigureVisible','off');

% 1. Lotka-Volterra: x'=4x-2xy, y'=xy-3y.
m='Q1_Lotka_Volterra'; fresh(m,'25');
blk(m,'simulink/Continuous/Integrator','x',[350 90 380 120],{'InitialCondition','2'});
blk(m,'simulink/Continuous/Integrator','y',[350 230 380 260],{'InitialCondition','3'});
blk(m,'simulink/Math Operations/Product','xy',[160 155 190 185],{});
blk(m,'simulink/Math Operations/Gain','4x',[170 65 225 95],{'Gain','4'});
blk(m,'simulink/Math Operations/Gain','minus2xy',[215 145 285 175],{'Gain','-2'});
blk(m,'simulink/Math Operations/Gain','minus3y',[170 285 240 315],{'Gain','-3'});
blk(m,'simulink/Math Operations/Sum','xdot',[305 75 325 105],{'Inputs','++'});
blk(m,'simulink/Math Operations/Sum','ydot',[305 215 325 245],{'Inputs','++'});
blk(m,'simulink/Sinks/To Workspace','x_data',[470 75 565 105],{'VariableName','x_data','SaveFormat','Timeseries'});
blk(m,'simulink/Sinks/To Workspace','y_data',[470 215 565 245],{'VariableName','y_data','SaveFormat','Timeseries'});
line(m,'x/1','4x/1'); line(m,'x/1','xy/1'); line(m,'y/1','xy/2');
line(m,'y/1','minus3y/1'); line(m,'xy/1','minus2xy/1');
line(m,'4x/1','xdot/1'); line(m,'minus2xy/1','xdot/2');
line(m,'xy/1','ydot/1'); line(m,'minus3y/1','ydot/2');
line(m,'xdot/1','x/1'); line(m,'ydot/1','y/1');
line(m,'x/1','x_data/1'); line(m,'y/1','y_data/1');
save_system(m); s=sim(m); x=s.x_data; y=s.y_data;
f=figure; tiledlayout(1,2); nexttile; plot(x.Time,x.Data,y.Time,y.Data); legend('x','y'); xlabel('t (s)'); ylabel('population'); grid on;
nexttile; plot(x.Data,y.Data); xlabel('x'); ylabel('y'); axis tight; grid on; saveas(f,'Q1.png'); close(f);

% 2. Van der Pol: y''=(1-y^2)y'-y.
m='Q2_Van_der_Pol'; fresh(m,'30');
blk(m,'simulink/Continuous/Integrator','ydot',[360 85 390 115],{'InitialCondition','0'});
blk(m,'simulink/Continuous/Integrator','y',[460 85 490 115],{'InitialCondition','2'});
blk(m,'simulink/Math Operations/Math Function','square',[145 170 205 200],{'Operator','square'});
blk(m,'simulink/Sources/Constant','one',[130 235 170 265],{'Value','1'});
blk(m,'simulink/Math Operations/Sum','one_minus_y2',[230 205 260 235],{'Inputs','+-'});
blk(m,'simulink/Math Operations/Product','product',[280 185 310 215],{});
blk(m,'simulink/Math Operations/Sum','accel',[325 70 345 100],{'Inputs','+-'});
blk(m,'simulink/Sinks/To Workspace','y_data',[540 70 630 100],{'VariableName','y_data','SaveFormat','Timeseries'});
blk(m,'simulink/Sinks/To Workspace','v_data',[450 165 540 195],{'VariableName','v_data','SaveFormat','Timeseries'});
line(m,'one/1','one_minus_y2/1'); line(m,'y/1','square/1'); line(m,'square/1','one_minus_y2/2');
line(m,'one_minus_y2/1','product/1'); line(m,'ydot/1','product/2');
line(m,'product/1','accel/1'); line(m,'y/1','accel/2'); line(m,'accel/1','ydot/1'); line(m,'ydot/1','y/1');
line(m,'y/1','y_data/1'); line(m,'ydot/1','v_data/1');
save_system(m); s=sim(m); y=s.y_data; v=s.v_data;
f=figure; tiledlayout(1,2); nexttile; plot(y.Time,y.Data,v.Time,v.Data); legend('y','dy/dt'); xlabel('t (s)'); grid on;
nexttile; plot(y.Data,v.Data); xlabel('y'); ylabel('dy/dt'); grid on; saveas(f,'Q2.png'); close(f);

% 3. Motor G(s)=1/(0.5s^2+5s). Unity feedback, filtered PD.
G3=tf(1,[.5 5 0]); C3=tf([15 250],[.005 1]); T3=feedback(C3*G3,1);
i3open=stepinfo(feedback(G3,1)); i3=stepinfo(T3);
control_model('Q3_Motor',G3,C3,'5');
plot_control(T3,'Q3');
t=(0:.002:5)'; u=cos(t)+exp(-3*t); yy=lsim(T3,u,t);
f=figure; plot(t,u,t,yy); legend('input','output'); xlabel('t (s)'); grid on; saveas(f,'Q3_input.png'); close(f);
control_forcing('Q3_Composite',G3,C3,t,u);
ti=(0:.0005:2)'; ui=500*double(ti<.002); % Unit-area, 2 ms pulse approximates an impulse.
control_forcing('Q3_Impulse',G3,C3,ti,ui);

% 4. Two-mass system, explicit self-chosen parameters.
M1=1; M2=1; b1=2; b2=1; k=10;
A=[0 1 0 0;0 -(b1+b2)/M1 0 b1/M1;0 0 0 1;0 b1/M2 -k/M2 -b1/M2];
B=[0;1/M1;0;0]; C=[1 0 0 0]; G4=minreal(tf(ss(A,B,C,0)));
% Filtered PD gains tuned against the stated 10--90% rise and 2% settling definitions.
C4=tf([12 45],[.01 1]); T4=feedback(C4*G4,1);
i4=stepinfo(T4); p4=pole(G4); p4closed=pole(T4);
control_model('Q4_Two_Mass',G4,C4,'12');
plot_control(T4,'Q4');
f=figure; step(G4,15); grid on; title('Q4 open-loop step response'); saveas(f,'Q4_open.png'); close(f);

fid=fopen('results.txt','w','n','UTF-8');
fprintf(fid,'Q1: x(0)=2, y(0)=3; closed periodic Lotka-Volterra orbit about (3,2).\n');
fprintf(fid,'Q2: y(0)=2, y''(0)=0; trajectory approaches a stable limit cycle.\n');
fprintf(fid,'Q3 open unity feedback: rise %.6g s, settle %.6g s, overshoot %.6g%%.\n',i3open.RiseTime,i3open.SettlingTime,i3open.Overshoot);
fprintf(fid,'Q3 C(s)=(15s+250)/(.005s+1): rise %.6g s, settle %.6g s, overshoot %.6g%%.\n',i3.RiseTime,i3.SettlingTime,i3.Overshoot);
fprintf(fid,'Q4 parameters M1=%g,M2=%g,b1=%g,b2=%g,k=%g.\n',M1,M2,b1,b2,k);
fprintf(fid,'Q4 open poles: %s.\n',mat2str(p4,5));
fprintf(fid,'Q4 C(s)=(12s+45)/(.01s+1): rise %.6g s, settle %.6g s, overshoot %.6g%%.\n',i4.RiseTime,i4.SettlingTime,i4.Overshoot);
fprintf(fid,'Q4 closed poles: %s.\n',mat2str(p4closed,5));
fclose(fid);
assert(i3.RiseTime<.1 && i3.SettlingTime<.8 && i3.Overshoot<10,'Q3 specifications failed');
assert(i4.RiseTime<.5 && i4.SettlingTime<4 && i4.Overshoot<10,'Q4 specifications failed');
disp(fileread('results.txt'));
end

function fresh(m,stop)
if bdIsLoaded(m), close_system(m,0); end
new_system(m); set_param(m,'StopTime',stop,'Solver','ode45','RelTol','1e-8','AbsTol','1e-10');
end
function blk(m,lib,name,pos,props)
add_block(lib,[m '/' name],'Position',pos);
if ~isempty(props), set_param([m '/' name],props{:}); end
end
function line(m,a,b)
add_line(m,a,b,'autorouting','on');
end
function control_model(m,p,c,stop)
fresh(m,stop);
[pn,pd]=tfdata(p,'v'); [cn,cd]=tfdata(c,'v');
blk(m,'simulink/Sources/Step','reference',[40 85 70 115],{});
blk(m,'simulink/Math Operations/Sum','error',[105 85 135 115],{'Inputs','+-'});
blk(m,'simulink/Continuous/Transfer Fcn','controller',[170 85 260 115],{'Numerator',mat2str(cn),'Denominator',mat2str(cd)});
blk(m,'simulink/Continuous/Transfer Fcn','plant',[300 85 390 115],{'Numerator',mat2str(pn),'Denominator',mat2str(pd)});
blk(m,'simulink/Sinks/To Workspace','output',[440 85 520 115],{'VariableName','response','SaveFormat','Timeseries'});
line(m,'reference/1','error/1'); line(m,'error/1','controller/1'); line(m,'controller/1','plant/1'); line(m,'plant/1','output/1'); line(m,'plant/1','error/2');
save_system(m); sim(m);
end
function plot_control(T,prefix)
f=figure; step(T,5); grid on; title([prefix ' closed-loop step']); saveas(f,[prefix '_step.png']); close(f);
f=figure; impulse(T,2); grid on; title([prefix ' closed-loop impulse']); saveas(f,[prefix '_impulse.png']); close(f);
end
function control_forcing(m,p,c,t,u)
fresh(m,num2str(t(end)));
[pn,pd]=tfdata(p,'v'); [cn,cd]=tfdata(c,'v');
input_signal=timeseries(u,t);
blk(m,'simulink/Sources/From Workspace','input',[40 85 100 115],{'VariableName','input_signal'});
blk(m,'simulink/Math Operations/Sum','error',[135 85 165 115],{'Inputs','+-'});
blk(m,'simulink/Continuous/Transfer Fcn','controller',[200 85 290 115],{'Numerator',mat2str(cn),'Denominator',mat2str(cd)});
blk(m,'simulink/Continuous/Transfer Fcn','plant',[330 85 420 115],{'Numerator',mat2str(pn),'Denominator',mat2str(pd)});
blk(m,'simulink/Sinks/To Workspace','output',[470 85 550 115],{'VariableName','response','SaveFormat','Timeseries'});
line(m,'input/1','error/1'); line(m,'error/1','controller/1'); line(m,'controller/1','plant/1'); line(m,'plant/1','output/1'); line(m,'plant/1','error/2');
% Store the input inside the model workspace for independent reruns.
mw=get_param(m,'ModelWorkspace'); assignin(mw,'input_signal',input_signal);
save_system(m); sim(m);
end
