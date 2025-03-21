$$
\newcommand{\dt}{\Delta t \,}
\newcommand{\VelocL}{\bm{w}}
\newcommand{\velmat}{\bm{w}}
\newcommand{\velspa}{\bm{\omega}}
\newcommand{\VelocR}{\bm{\omega}}
\newcommand{\DisplR}{\bm{\Lambda}}
\newcommand{\matmom}{\bm{\Pi}}
\newcommand{\momspa}{\bm{\pi}}
\newcommand{\accspa}{\bm{\alpha}}
\newcommand{\accmat}{\bm{a}}
\newcommand{\inrmat}{\mathbb{J}}
% \newcommand{\inrmat}{\mathbf{I}}
$$

 In [LS94b], Lewis and Simo present a symplectic, energy and momentum-preserving integrator for the free rigid body which encompasses,
as a particular case, the energy-momentum algorithms of Simo and Wong [SW91] and the
midpoint-rule integrator of Austin et al. [AKW93], with the further property that the scheme
is symplectic.


----------------


In a famous paper, Moser and
Veselov [MV91] derive an integrator for the free rigid body by embedding SO(3) in the linear
space of 3 × 3 matrices and using Lagrange multipliers to constrain the body configuration
to SO(3). The discrete Moser-Veselov is a particular case of the RATTLE algorithm for matrix Lie groups [MS95, MZ05]. The RATTLE scheme is a classical method for the integration
of constrained Hamiltonian systems. Its application to matrix Lie group, and in particular
to rigid body integration, was proposed independently by Reich [Rei94] and McLachlan and
Scovel [MS95]. This method is symplectic and momentum-preserving both for the free body
case and the generic potential case, and exactly preserves energy only in the former case.


----------------


$$
\begin{aligned}
\dot{\pi} & =\frac{\mathrm{d}}{\mathrm{~d} t}\left[\mathbf{I}_t \velspa\right] \\
& =\dot{\mathbf{I}}_t \velspa+\mathbf{I}_{\mathbf{t}} \dot{\velspa} \\
& =\velspa \times \mathbb{I}_t \velspa+\mathbf{I}_t \dot{\velspa}=\overline{\mathbf{m}}
\end{aligned}
$$

Convected description

$$
\begin{aligned}
\inrmat \dot{\velmat} + \velmat \times \inrmat \velmat & = \boldsymbol{\Lambda}^{\mathrm{t}} \overline{\mathbf{m}} \\
\dot{\boldsymbol{\Lambda}} & =\boldsymbol{\Lambda} \velmat^{\times} \\
\end{aligned}
\qquad
\begin{aligned}
& \mathbf{I}_{\mathbf{t}} \dot{\velspa} + \velspa \times \mathbf{I}_{\mathbf{t}} \velspa = \overline{\mathbf{m}} = \dot{\momspa} \\
& \dot{\mathbf{\Lambda}}= \velspa^{\times} \mathbf{\Lambda} \\
\end{aligned}
$$


$$
\momspa \bigl(\bm{\Lambda}(t), \velmat(t)\bigr) = \mathbf{\Lambda} \matmom
=\mathbf{\Lambda} \inrmat \velmat
$$

$$
\begin{aligned} 
& \dot{\matmom}
=-\left[\mathbf{I}^{-1} \matmom \right] \times \matmom +\mathbf{T} \\ 
& \dot{\bm{\Psi}}=\left(d \exp _{-\Psi}\right)^{-1} \mathbf{I}^{-1} \matmom
\end{aligned}
$$

## Simo 

![alt text](images/SW.png)

### SQ-M (`ALGO_0`)

### SW-M (`ALGO_1`)
$$
\begin{aligned}
\bm{g}(\bm{y}) &= \dot{\momspa} (\tilde{\chi} \circ \bm{y}) - \bm{m}\bigl(\tilde{t}\bigr) \\
\tilde{\bm{\Lambda}} &= 
\end{aligned}
$$

### SW-C (`ALCO_C1`)

$$
\begin{aligned}
\bm{g}(\bm{y}) &= \momspa (\tilde{\chi} \circ \bm{y})  - \momspa_0 - \dt \bm{m} \\
\tilde{\bm{\Lambda}} &= 
\end{aligned}
$$

$$
\text{Given }\boldsymbol{\Pi}_{n-1}, \mathbf{R}_{n-1} \text{ 
Solve as a coupled system of equations} 
$$
$$
\boxed{
\begin{aligned}
\boldsymbol{\Psi}_n&=\frac{\Delta t}{2}\left(\mathbf{I}^{-1} \boldsymbol{\Pi}_n+\mathbf{I}^{-1} \boldsymbol{\Pi}_{n-1}\right) \\
\bm{R}_n&=\bm{R}_{n-1} \exp \left[\boldsymbol{\Psi}_n\right] \\
\boldsymbol{\Pi}_n &= \exp \left[-\boldsymbol{\Psi}_n \right] \boldsymbol{\Pi}_{n-1}+\Delta t \exp \left[-\frac{1}{2} \boldsymbol{\Psi}_n\right] \mathbf{T}_{n-1 / 2}
\end{aligned}
}
$$


![alt text](images/image-3.png)

![alt text](images/image.png)

### SVQ-VLN (ELN)

$$
\left\{\begin{aligned}
\boldsymbol{\Omega}_{k+\frac{1}{2}} & =\boldsymbol{\Omega}_k+\frac{h}{2} \mathbf{J}^{-1}\left(\mathbf{J} \boldsymbol{\Omega}_k \times \boldsymbol{\Omega}_k+\boldsymbol{\tau}\left(\mathbf{Q}_k\right)\right) \\
\mathbf{Q}_{k+1} & =\mathbf{Q}_k \operatorname{cay}\left(\dt \boldsymbol{\Omega}_{k+\frac{1}{2}}\right), \\
\boldsymbol{\Omega}_{k+1} & =\boldsymbol{\Omega}_{k+\frac{1}{2}}+\tfrac{1}{2} \dt \mathbf{J}^{-1}\left(\mathbf{J} \boldsymbol{\Omega}_{k+1} \times \boldsymbol{\Omega}_{k+1}+\tau\left(\mathbf{Q}_{k+1}\right)\right)
\end{aligned}\right.
$$

### SVQ-TLN

$$
\left\{\begin{array}{l}
\left(I+\frac{h}{2} \widehat{\boldsymbol{\Omega}}_{k+1}\right) \mathbf{J} \boldsymbol{\Omega}_{k+1}-\frac{h}{2} \boldsymbol{\tau}\left(\mathbf{Q}_{k+1}\right)=\left(I-\frac{h}{2} \widehat{\boldsymbol{\Omega}}_k\right) \mathbf{J} \boldsymbol{\Omega}_k+\frac{h}{2} \boldsymbol{\tau}\left(\mathbf{Q}_k\right), \\
\mathbf{Q}_{k+1}=\mathbf{Q}_k \operatorname{cay}\left(h \frac{\boldsymbol{\Omega}_k+\boldsymbol{\Omega}_{k+1}}{2}\right) .
\end{array}\right.
$$

$$
f(\boldsymbol{\omega})
=-\mathbf{J} \boldsymbol{\omega}-\frac{1}{2} \dt \, \boldsymbol{\omega} {\times} \boldsymbol{J} \boldsymbol{\omega}+\frac{h}{2} \tau\left(G_k(\boldsymbol{\omega})\right)+\left(I-\frac{h}{2} \hat{\boldsymbol{\omega}}_k\right) \mathrm{J} \boldsymbol{\omega}_k+\frac{h}{2} \tau\left(\mathbf{R}_k\right) .
$$
$$
\begin{aligned}
& J_f\left(\boldsymbol{\omega}^n\right)=-\mathbf{J}-\frac{h}{2}\left[\left(\mathbf{J} \boldsymbol{\omega}^n\right)^{\wedge}+\hat{\boldsymbol{\omega}}^n \mathbf{J}\right]+ \\
& +\frac{h^2}{2\left(m_I\left(G_k\left(\boldsymbol{\omega}^n\right)\right)\right)^3}\left[\begin{array}{c}
\operatorname{tr}\left(G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_1\right) \\
\operatorname{tr}\left(G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_2\right) \\
\operatorname{tr}\left(G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_3\right)
\end{array}\right]\left[\begin{array}{c}
\operatorname{tr}\left(G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_1\right) \\
\operatorname{tr}\left(G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_2\right) \\
\operatorname{tr}\left(G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_3\right)
\end{array}\right]^T \operatorname{cay}\left(-h \frac{\boldsymbol{\omega}_k+\boldsymbol{\omega}^n}{2}\right) \mathrm{dcay}_{h \frac{\omega_k+\omega^n}{2}}^2+ \\
& +\frac{h^2}{2}\left[1-\frac{1}{m_{\mathrm{I}}\left(G_k\left(\boldsymbol{\omega}^n\right)\right)}\right]\left[\operatorname{tr}\left(\mathbf{R}_k\left(\operatorname{dcay}_{h \frac{\omega_k+\omega^n}{2}} \cdot e_j\right)^{\wedge} \operatorname{cay}\left(h \frac{\boldsymbol{\omega}_k+\boldsymbol{\omega}^n}{2}\right) \hat{e}_i\right)\right]_{i j}+ \\
& +\frac{3 h^2 \alpha}{4\left(m_{\mathbf{R}_m}\left(G_k\left(\boldsymbol{\omega}^n\right)\right)\right)^5}\left[\begin{array}{c}
\operatorname{tr}\left(\mathbf{R}_m^T G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_1\right) \\
\operatorname{tr}\left(\mathbf{R}_m^T G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_2\right) \\
\operatorname{tr}\left(\mathbf{R}_m^T G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_3\right)
\end{array}\right]\left[\begin{array}{c}
\operatorname{tr}\left(\mathbf{R}_m^T G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_1\right) \\
\operatorname{tr}\left(\mathbf{R}_m^T G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_2\right) \\
\operatorname{tr}\left(\mathbf{R}_m^T G_k\left(\boldsymbol{\omega}^n\right) \hat{e}_3\right)
\end{array}\right]^T \operatorname{cay}\left(-h \frac{\boldsymbol{\omega}_k+\boldsymbol{\omega}^n}{2}\right) \mathrm{dcay}_{h \frac{\omega_k+\omega^n}{2}}^2+ \\
& +\frac{h^2 \alpha}{4\left(m_{\mathbf{R}_m}\left(G_k\left(\boldsymbol{\omega}^n\right)\right)\right)^3}\left[\operatorname{tr}\left(\mathbf{R}_m^T \mathbf{R}_k\left(\operatorname{dcay}_{h \frac{\omega_k+\omega^n}{2}} \cdot e_j\right)^{\wedge} \operatorname{cay}\left(h \frac{\boldsymbol{\omega}_k+\boldsymbol{\omega}^n}{2}\right) \hat{e}_i\right)\right]_{i j},
\end{aligned}
$$

## Explicit

![alt text](./images/image-4.png)

![alt text](./images/image-6.png)


### TRAP

$$
\begin{aligned}
\matmom_{t+\Delta t} 
&=\matmom_t+\frac{1}{2}\Delta t \left(
    -\left[\mathbf{I}^{-1} \matmom_t           \right]^{\times} \matmom_t+\mathbf{T}_t
    -\left[\mathbf{I}^{-1} \matmom_{t+\Delta t}\right]^{\times} \matmom_{t+\Delta t}+\mathbf{T}_{t+\Delta t}
\right) \\
\boldsymbol{\Psi}_{t+\Delta t / 2} &=\frac{\Delta t}{2} \mathbf{I}^{-1} \matmom_t, \\
\boldsymbol{\Psi}_{t+\Delta t}     &=\frac{\Delta t}{2} \mathbf{I}^{-1} \matmom_{t+\Delta t}
\end{aligned}
$$

$$
\begin{aligned}
\matmom_{t+\Delta t} 
&=\matmom_t+\frac{1}{2}\Delta t \left(
    -\operatorname{skew}\left[\mathbf{I}^{-1} \matmom_t           \right] \matmom_t+\mathbf{T}_t
    -\operatorname{skew}\left[\mathbf{I}^{-1} \matmom_{t+\Delta t}\right] \matmom_{t+\Delta t}+\mathbf{T}_{t+\Delta t}
\right) \\
\boldsymbol{\Psi}_{t+\Delta t / 2} &=\frac{\Delta t}{2} \mathbf{I}^{-1} \matmom_t, \\
\boldsymbol{\Psi}_{t+\Delta t}     &=\frac{\Delta t}{2} \mathbf{I}^{-1} \matmom_{t+\Delta t}
\end{aligned}
$$

![alt text](images/image-1.png)

### `RKMK`

![alt text](images/image-7.png)

### `LIEMID`

![alt text](images/image-6.png)

### `LIEMID[I]` (`IMIDM`)

![alt text](images/image-4.png)
![alt text](images/image-5.png)

RKMK with tableau:
$$
\begin{array}{c|c}
1 / 2 & 1 / 2 \\
\hline & 1
\end{array}
$$

---------

![alt text](./images/LIEMIDE.png)

![alt text](./images/image-3.png)

![alt text](./images/image-2.png)

### `RKMK-TRAP`

![alt text](images/image-2.png)

$$
\left\{\begin{array}{l}
\boldsymbol{\omega}_{k+\frac{1}{2}}=\boldsymbol{\omega}_k+\frac{h}{2} \boldsymbol{J}^{-1}\left(\tau\left(\mathbf{R}_k\right)-\boldsymbol{\omega}_{k+\frac{1}{2}} \times \mathbf{J} \boldsymbol{\omega}_{k+\frac{1}{2}}\right) \\
\mathbf{R}_{k+1}=\mathbf{R}_k \operatorname{cay}\left(\dt  \boldsymbol{\omega}_{k+\frac{1}{2}}\right) \\
\boldsymbol{\omega}_{k+1}=\boldsymbol{\omega}_{k+\frac{1}{2}}+\frac{h}{2} \mathbf{J}^{-1}\left(\tau\left(\mathbf{R}_{k+1}\right)-\boldsymbol{\omega}_{k+\frac{1}{2}} \times \mathbf{J} \boldsymbol{\omega}_{k+\frac{1}{2}}\right)
\end{array}\right.
$$

### `VLV`

$$
\left\{\begin{array}{l}
\boldsymbol{\omega}_{k+\frac{1}{2}}=\boldsymbol{\omega}_k+\frac{h}{2} \mathbf{J}^{-1}\left[\mathbf{J} \boldsymbol{\omega}_{k+\frac{1}{2}} \times \boldsymbol{\omega}_{k+\frac{1}{2}}-\frac{h}{2}\left(\boldsymbol{\omega}_{k+\frac{1}{2}}^T \mathbf{J} \boldsymbol{\omega}_{k+\frac{1}{2}}\right) \boldsymbol{\omega}_{k+\frac{1}{2}}+\tau\left(\mathbf{R}_k\right)\right] \\
\mathbf{R}_{k+1}=\mathbf{R}_k \operatorname{cay}\left(h \boldsymbol{\omega}_{k+\frac{1}{2}}\right) \\
\boldsymbol{\omega}_{k+1}=\boldsymbol{\omega}_{k+\frac{1}{2}}+\frac{h}{2} \mathbf{J}^{-1}\left[\mathbf{J} \boldsymbol{\omega}_{k+\frac{1}{2}} \times \boldsymbol{\omega}_{k+\frac{1}{2}}+\frac{h}{2}\left(\boldsymbol{\omega}_{k+\frac{1}{2}}^T \mathbf{J} \boldsymbol{\omega}_{k+\frac{1}{2}}\right) \boldsymbol{\omega}_{k+\frac{1}{2}}+\tau\left(\mathbf{R}_{k+1}\right)\right]
\end{array}\right.
$$
Solve:
$$
f(\boldsymbol{\omega})=-\boldsymbol{\omega} + \boldsymbol{\omega}_{k+\frac{1}{2}}+\tfrac{1}{2} \dt \left[(\mathbf{J} \boldsymbol{\omega}) \times \boldsymbol{\omega} - \tfrac{1}{2} \dt \left(\boldsymbol{\omega} \cdot \mathbf{J} \boldsymbol{\omega}\right) \boldsymbol{\omega}+\tau(\mathbf{R})\right]
$$
with Jacobian:
$$
J_f(\boldsymbol{\omega})=-\mathbf{I}+\frac{h}{2} \mathbf{J}^{-1}\left[(\mathbf{J} \boldsymbol{\omega})^{\wedge}-\hat{\boldsymbol{\omega}} \mathbf{J}-h \xi \boldsymbol{\omega}^T \mathbf{J}-\frac{h}{2}\left(\boldsymbol{\omega}^T \mathbf{J} \boldsymbol{\omega}\right) \mathbf{I}\right]
$$

### `LIEMID[EA]`

![alt text](images/LIEMIDEA.png)

$$
\left\{\begin{aligned}
\boldsymbol{\Theta}_{k+\frac{1}{2}} & =\tfrac{1}{2} \dt \mathbf{J}^{-1} \exp \left(-\frac{1}{2} \boldsymbol{\Theta}_{k+\frac{1}{2}}\right)\left(\mathbf{J} \boldsymbol{\Omega}_k+\frac{h}{2} \boldsymbol{\tau}\left(\mathbf{Q}_k\right)\right) \\
\mathbf{Q}_{k+\frac{1}{2}} & =\mathbf{Q}_k \exp \left(\boldsymbol{\Theta}_{k+\frac{1}{2}}\right), \\
\boldsymbol{\Omega}_{k+\frac{1}{2}} & =\mathbf{J}^{-1} \exp \left(-\boldsymbol{\Theta}_{k+\frac{1}{2}}\right)\left(\mathbf{J} \boldsymbol{\Omega}_k+\frac{h}{2} \boldsymbol{\tau}\left(\mathbf{Q}_k\right)\right), \\
\boldsymbol{\Theta}_{k+1} & =\frac{h}{2} \mathbf{J}^{-1} \exp \left(-\frac{1}{2} \boldsymbol{\Theta}_{k+1}\right) \mathbf{J} \boldsymbol{\Omega}_{k+\frac{1}{2}}, \\
\mathbf{Q}_{k+1} & =\mathbf{Q}_{k+\frac{1}{2}} \exp \left(\boldsymbol{\Theta}_{k+1}\right), \\
\boldsymbol{\Omega}_{k+1} & =\mathbf{J}^{-1}\left(\exp \left(-\boldsymbol{\Theta}_{k+1}\right) \mathbf{J} \boldsymbol{\Omega}_{k+\frac{1}{2}}+\frac{h}{2} \boldsymbol{\tau}\left(\mathbf{Q}_{k+1}\right)\right),
\end{aligned}\right.
$$

---------------


![alt text](./images/HSTAGM.png)


bb_rkmk_trap
bb_rkmk_trap_wdexp
dyneq_imid
dyneq_imidm
dyneq_trap
dyneq_trapm
dyneq_trapm_zeta
IncrSO3_AKW
LIEMIDEA
liemid_Newmark
mleok
rotint_nmb
simo_wong_algo_c1
simo_wong_algo_c2
SVQ
VLV
