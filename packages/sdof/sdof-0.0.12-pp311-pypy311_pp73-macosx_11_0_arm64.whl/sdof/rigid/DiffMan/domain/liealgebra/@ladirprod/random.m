function z = random(obj)
% RANDOM - Creates a random object in the Lie algebra 'ladirprod'.
% function z = random(obj)

% WRITTEN BY       : Kenth Eng�, 1997 Oct.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.12

z = ladirprod(obj);
if iscellempty(obj(1).shape), z = obj; return; end;

for i = 1:length(obj), % For the case: vectors of objects.
  sh = obj(i).shape;
  for j = 1:obj(i).n
    z(i).data{j} = ladprandom(sh{2}(j,:));
  end;
end;
return;
