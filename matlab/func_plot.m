%%
clear; close all;

%
figure;
hold on;
fplot(@(u) 12.92 * u ^ 2 + 5, [0 3300], 'g', 'DisplayName', 'org');
fplot(@(u) 12.92 * (u - 100) ^ 2 + 5, [0 3300], 'r', 'DisplayName', 'sft');
fplot(@(u) (12.92 * u ^ 2 + 5) * 0.787416851, [0 3300], 'y', 'DisplayName', 'multi');
fplot(@(u) (12.92 * u ^ 2 + 5) + 10000000, [0 3300], 'b', 'DisplayName', 'add');
hold off;
legend show;
figureHandle = gcf;
save_name = '/home/manu/tmp/calc.png';
title(save_name);
saveas(figureHandle, save_name);

%%
