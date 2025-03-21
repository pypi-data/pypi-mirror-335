function Out = set(sys,varargin)
%SET  Set properties of LTI model SYS.
%
%   SET(SYS,'Property',VALUE)  sets the property of SYS specified
%   by the string 'Property' to the value VALUE.
%
%   SET(SYS,'Property1',Value1,'Property2',Value2,...)  sets multiple 
%   LTI property values with a single statement.
%
%   SET(SYS,'Property')  displays possible values for the specified
%   property of SYS.
%
%   SET(SYS)  displays all properies of SYS and their admissible 
%   values.
%
%   Note:  Resetting the sampling time does not alter the state-space
%          matrices.  Use C2D or D2D for conversion purposes.
%
%   See also  GET, SS, TF, ZPK.

%       Author(s): A. Potvin, 3-1-94, P. Gahinet, 4-1-96
%       Copyright (c) 1986-96 by The MathWorks, Inc.
%       $Revision: 1.1 $  $Date: 1997/10/14 15:09:08 $

ni = nargin;
no = nargout;
if ~isa(sys,'tf'),
   % Call built-in SET. Handles calls like set(gcf,'user',tf)
   builtin('set',sys,varargin{:});
   return
elseif no & ni>1,
   error('Output argument allowed only in SET(SYS)');
end

% Get TF properties
[Props,PValues] = pvpget('tf');

% Return Props and set nothing if nargin<=2
if ni==1,
   if no,
     Out = cell2struct(PValues,Props,1);
   else
     pvpdisp(Props,PValues,':  ');
   end
   return
elseif ni==2,
   str = varargin{1};
   if ~isstr(str),
      error('Property names must be single-line strings');
   end
   % Return admissible property value(s)
   [ind,stat] = pmatch(Props,str);
   error(stat);
   if no,
      Out = PValues{ind};
   else
      disp(PValues{ind});
   end
   return
elseif no,
   error('No output argument when called with PV pairs')
elseif rem(ni-1,2)~=0,
   error('Property/Value pairs must come in even number');
end

% Now we have set(sys,P1,V1, ...)
name = inputname(1);
if isempty(name),
   error('First argument to set must be a named variable')
end
numden = 0;
SetTs = 0;
SetVar = 0;
L = sys.lti;

for i=1:2:ni-1,
   % Set each PV pair in turn
   [ind,stat] = pmatch(Props,varargin{i});
   error(stat);
   if length(ind)>1,
     error('Property names must be single-line strings');
   end
   Property = Props{ind};
   Value = varargin{i+1};
   
   switch Property
   case 'num'
      if isa(Value,'double'),  Value = {Value};  end
      sys.num = Value;   
      numden = numden + 1;
   case 'den'
      if isa(Value,'double'),  Value = {Value};  end
      sys.den = Value;
      numden = numden + 1;
   case 'Variable'
      if ~isstr(Value),
         error('Property "Variable" must be set to a string.');
      elseif isempty(strmatch(Value,{'s';'p';'z';'z^-1';'q'},'exact')),
         error('Invalid value for property "Variable"');
      end
      OldVar = sys.Variable;
      sys.Variable = Value;
      SetVar = 1;
   case 'Ts'
      set(L,'Ts',Value);
      SetTs = 1;
   otherwise
      set(L,Property,Value);
   end % switch
end % for



% EXIT CHECKS:
% (1) Variable vs. sampling time:
var = sys.Variable;
LL = struct(L);   % LTI structure
sp = strcmp(var,'s') | strcmp(var,'p');
Ts = LL.Ts;
if Ts==0 & ~sp,
   % First conflicting case: Ts = 0 with Variable 'z', 'z^-1', or 'q'
   if ~SetTs,
      % Variable 'z', 'q', 'z^-1' used to mean "discrete". Set Ts to -1
      LL.Ts = -1;    
      L = quickset(L,LL);
   else
      % Ts explicitly set to zero: reset Variable to default 's'
      sys.Variable = 's';
      if SetVar,
         warning(['Variable ' var ' inappropriate for continuous systems.'])
      end
   end
elseif Ts~=0 & sp,
   % Second conflicting case: nonzero Ts with Variable 's' or 'p'
   sys.Variable = 'z';   % default
   if SetVar,
      % Variable was set to 's' or 'p': revert to old value if adequate
      warning(['Variable ' var ' inappropriate for discrete systems.'])
      if ~isempty(strmatch(OldVar,{'z';'z^-1';'q'},'exact')),
         sys.Variable = OldVar;
      end
   end
end

% (2) NUM/DEN check and padding
if numden,
   error(ndcheck(sys.num,sys.den,numden));
   [sys.num,sys.den] = ndpad(sys.num,sys.den,sys.Variable);
end

% (3) Check LTI property consistency
[p,m] = size(sys.num);
[sys.lti,errmsg] = lticheck(L,p,m);
error(errmsg)

% Finally, assign sys in caller's workspace
assignin('caller',name,sys)

% end ../@tf/set.m
