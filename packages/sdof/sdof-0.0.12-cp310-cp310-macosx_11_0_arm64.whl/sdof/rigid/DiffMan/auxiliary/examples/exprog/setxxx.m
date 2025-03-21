function [] = setxxx(a,v)
%SETxxx set xxxdata given by value v in class element a
%
%   function [] = setxxx(a,v)
%
%  This is a sample m-file showing how properties can be set.
%
%  Example of usage:
%
%     �b.xxx = 'hans'
%     b = 
%         xxx: 'hans'
%     �setxxx(b,'anto')
%     �b
%     b = 
%         xxx: 'anto'

%       Author(s): H. Munthe-Kaas

error(nargchk(2,2,nargin));
error(nargchk(0,0,nargout));

name = inputname(1);
if isempty(name),
   error('First argument to set must be a named variable')
end

% plug in the value in a
a.xxx = v;

% Finally, assign a in caller's workspace
assignin('caller',name,a)


