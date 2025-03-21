# Newmark

$$
\begin{array}{l|ccc}
\tilde{\Gamma}_{ u u } & 0
     & 1
     & 1
\\[0.3cm]
\tilde{\Gamma}_{ u v } & 0
     & \frac{\Delta t \left(- \beta + \gamma\right)}{\gamma}
     & \Delta t
\\[0.3cm]
\tilde{\Gamma}_{ u a } & 0
     & \frac{\Delta t^{2} \left(- \beta + \frac{\gamma}{2}\right)}{\gamma}
     & \Delta t^{2} \left(\frac{1}{2} - \beta\right)
\\[0.3cm]
\tilde{\Gamma}_{ v u } & - \frac{\gamma}{\Delta t \beta}
     & 0
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ v v } & \frac{\beta - \gamma}{\beta}
     & 0
     & 1
\\[0.3cm]
\tilde{\Gamma}_{ v a } & \Delta t - \frac{\Delta t \gamma}{2 \beta}
     & 0
     & \Delta t \left(1 - \gamma\right)
\\[0.3cm]
\tilde{\Gamma}_{ a u } & - \frac{1}{\Delta t^{2} \beta}
     & 0
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ a v } & - \frac{1}{\Delta t \beta}
     & - \frac{1}{\Delta t \gamma}
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ a a } & \frac{\beta - \frac{1}{2}}{\beta}
     & \frac{\gamma - 1}{\gamma}
     & 0
\\[0.3cm]
\hline 
\tilde{\gamma}_{ u } & 1
     & \frac{\Delta t \beta}{\gamma}
     & \Delta t^{2} \beta

\\[0.3cm]
\tilde{\gamma}_{ v } & \frac{\gamma}{\Delta t \beta}
     & 1
     & \Delta t \gamma

\\[0.3cm]
\tilde{\gamma}_{ a } & \frac{1}{\Delta t^{2} \beta}
     & \frac{1}{\Delta t \gamma}
     & 1

\\[0.3cm]
\end{array}
$$

# Wilson

$$
\begin{array}{l|ccc}
\tilde{\Gamma}_{ u u } & 1 - \vartheta^{3}
     & 1
     & 1
\\[0.3cm]
\tilde{\Gamma}_{ u v } & \Delta t \vartheta \left(1 - \vartheta^{2}\right)
     & \frac{\Delta t \vartheta \left(- \beta \vartheta^{2} + \gamma\right)}{\gamma}
     & \Delta t \vartheta
\\[0.3cm]
\tilde{\Gamma}_{ u a } & \frac{\Delta t^{2} \vartheta^{2} \left(1 - \vartheta\right)}{2}
     & \frac{\Delta t^{2} \vartheta^{2} \left(- \beta \vartheta + \frac{\gamma}{2}\right)}{\gamma}
     & \Delta t^{2} \vartheta^{2} \left(- \beta \vartheta + \frac{1}{2}\right)
\\[0.3cm]
\tilde{\Gamma}_{ v u } & - \frac{\gamma \vartheta^{2}}{\Delta t \beta}
     & 0
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ v v } & \frac{\beta - \gamma \vartheta^{2}}{\beta}
     & 1 - \vartheta^{2}
     & 1
\\[0.3cm]
\tilde{\Gamma}_{ v a } & \frac{\Delta t \vartheta \left(2 \beta - \gamma \vartheta\right)}{2 \beta}
     & \Delta t \vartheta \left(1 - \vartheta\right)
     & \Delta t \vartheta \left(- \gamma \vartheta + 1\right)
\\[0.3cm]
\tilde{\Gamma}_{ a u } & - \frac{\vartheta}{\Delta t^{2} \beta}
     & 0
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ a v } & - \frac{\vartheta}{\Delta t \beta}
     & - \frac{\vartheta}{\Delta t \gamma}
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ a a } & \vartheta - \frac{\vartheta}{2 \beta}
     & \vartheta - \frac{\vartheta}{\gamma}
     & 0
\\[0.3cm]
\hline 
\tilde{\gamma}_{ u } & \vartheta^{3}
     & \frac{\Delta t \beta \vartheta^{3}}{\gamma}
     & \Delta t^{2} \beta \vartheta^{3}

\\[0.3cm]
\tilde{\gamma}_{ v } & \frac{\gamma \vartheta^{2}}{\Delta t \beta}
     & \vartheta^{2}
     & \Delta t \gamma \vartheta^{2}

\\[0.3cm]
\tilde{\gamma}_{ a } & \frac{\vartheta}{\Delta t^{2} \beta}
     & \frac{\vartheta}{\Delta t \gamma}
     & \vartheta

\\[0.3cm]
\end{array}
$$

# Alpha

$$
\begin{array}{l|ccc}
\tilde{\Gamma}_{ u u } & 1 - \alpha_{u}
     & 1
     & 1
\\[0.3cm]
\tilde{\Gamma}_{ u v } & 0
     & \frac{\Delta t \alpha_{u} \left(- \beta + \gamma\right)}{\gamma}
     & \Delta t \alpha_{u}
\\[0.3cm]
\tilde{\Gamma}_{ u a } & 0
     & \frac{\Delta t^{2} \alpha_{u} \left(- 2 \beta + \gamma\right)}{2 \gamma}
     & \frac{\Delta t^{2} \alpha_{u} \left(1 - 2 \beta\right)}{2}
\\[0.3cm]
\tilde{\Gamma}_{ v u } & - \frac{\alpha_{v} \gamma}{\Delta t \beta}
     & 0
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ v v } & - \frac{\alpha_{v} \gamma}{\beta} + 1
     & 1 - \alpha_{v}
     & 1
\\[0.3cm]
\tilde{\Gamma}_{ v a } & \frac{\Delta t \alpha_{v} \left(2 \beta - \gamma\right)}{2 \beta}
     & 0
     & \Delta t \alpha_{v} \left(1 - \gamma\right)
\\[0.3cm]
\tilde{\Gamma}_{ a u } & - \frac{\alpha_{a}}{\Delta t^{2} \beta}
     & 0
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ a v } & - \frac{\alpha_{a}}{\Delta t \beta}
     & - \frac{\alpha_{a}}{\Delta t \gamma}
     & 0
\\[0.3cm]
\tilde{\Gamma}_{ a a } & - \frac{\alpha_{a}}{2 \beta} + 1
     & - \frac{\alpha_{a}}{\gamma} + 1
     & 1 - \alpha_{a}
\\[0.3cm]
\hline 
\tilde{\gamma}_{ u } & \alpha_{u}
     & \frac{\Delta t \alpha_{u} \beta}{\gamma}
     & \Delta t^{2} \alpha_{u} \beta

\\[0.3cm]
\tilde{\gamma}_{ v } & \frac{\alpha_{v} \gamma}{\Delta t \beta}
     & \alpha_{v}
     & \Delta t \alpha_{v} \gamma

\\[0.3cm]
\tilde{\gamma}_{ a } & \frac{\alpha_{a}}{\Delta t^{2} \beta}
     & \frac{\alpha_{a}}{\Delta t \gamma}
     & \alpha_{a}

\\[0.3cm]
\end{array}
$$

