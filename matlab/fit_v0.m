%% 
close all;

%%
% X = [2400, 2269, 2226, 2178, 2090, 2048, 1987, 1884, 1806, 1749, 1683, 1620, 1570, 1509, 1451, 1389, 1290, 1216, 1176, 1117, 1051, 1029;
%     2366, 2227, 2184, 2134, 2044, 2000, 1937, 1828, 1749, 1689, 1622, 1560, 1510, 1449, 1391, 1326, 1223, 1148, 1106, 1045, 976, 954;
%     2401, 2265, 2221, 2173, 2086, 2042, 1980, 1878, 1799, 1742, 1675, 1613, 1566, 1505, 1448, 1385, 1287, 1214, 1173, 1116, 1050, 1026;
%     2390, 2239, 2192, 2136, 2041, 1992, 1926, 1811, 1724, 1660, 1589, 1522, 1472, 1405, 1345, 1278, 1170, 1091, 1047, 983, 911, 885];
% y = [0, 60, 80, 100, 140, 158, 178, 219, 250, 265, 285, 303, 318, 340, 358, 378, 415, 438, 451, 472, 495, 500];

X = [682,981,1203,1359,1390,1419,1458,1485,1516,1540,1567,1592,1614,1737,1788,1815,1746];
Y = [55,81,116,156,161,177,190,200,210,221,228,239,248,273,289,308,341];

% X = [0, 682,981,1203,1359,1390,1419,1458,1485,1516,1540,1567,1592,1614,1737,1788,1815,1746, 1795, 1843, 1890, 3300];
% Y = [0, 55,81,116,156,161,177,190,200,210,221,228,239,248,273,289,308,341,380, 420, 460, 500];

p = polyfit(X, Y, 1);

Y_fit = polyval(p, X);

plot(X, Y, 'o', X, Y_fit, '-');

fprintf('%.32f\n', p);

% figure;
hold on;
X = 1:3300;
Y_pred = polyval(p, X);
plot(X, Y_pred);
hold off;
ylim([-100 600])

%%