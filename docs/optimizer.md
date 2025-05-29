# Bayesian Optimization in Traffic Simulation Calibration

This document explains how Bayesian Optimization is used to calibrate vehicle parameters in a traffic simulation pipeline based on real detector data.

---

## 📌 What is Bayesian Optimization?

Bayesian Optimization is a global optimization method designed for expensive-to-evaluate functions. It works by:

- Building a **probabilistic model** (usually a Gaussian Process) of the function to optimize.
- Using an **acquisition function** to decide where to sample next based on this model.

---

## 🎯 Why Use It in Our Project?

- Running a SUMO + TraCI simulation is **computationally expensive**.
- We want to optimize **departure time** and **speed factor** for each vehicle.
- Bayesian Optimization allows us to **find good parameters efficiently**, with fewer simulations.

---

## 📚 Bayesian Inference Recap

- **θ**: Parameters (e.g., depart time, speed factor)
- **D**: Observed data (detector times/speeds)
- **P(θ)**: Prior belief
- **P(D|θ)**: Likelihood
- **P(θ|D)**: Posterior (what we want)
- **P(D)**: Evidence (normalizer)

---

## 📐 Gaussian Process (GP)

GP models the unknown function with:

- A **mean function** (often zero)
- A **kernel** (covariance function)

### Common Kernel (RBF):
$$
k(x, x') = \exp\left(-\frac{\|x - x'\|^2}{2\ell^2}\right)
$$

Where \( \ell \) is the length scale controlling smoothness.

---

## 🔢 Posterior Prediction in GP

Given data $' X = [x_1, ..., x_n] '$, targets $' y '$, and new point $' x^* '$:

- $' K '$: Covariance matrix of training points
- $' k_* '$: Covariance vector between $' x^* '$ and training data

### Mean:
$$
\mu(x^*) = k_*^T K^{-1} y
$$

### Variance:
$$
\sigma^2(x^*) = k(x^*, x^*) - k_*^T K^{-1} k_*
$$

---

## 🎯 Acquisition Functions

Acquisition functions guide where to sample next.

### 1. **Expected Improvement (EI)**:
$$
EI(x) = \mathbb{E}[\max(0, f_{best} - f(x))]
$$

### 2. **Probability of Improvement (PI)**:
$$
PI(x) = \Phi\left(\frac{f_{best} - \mu(x)}{\sigma(x)}\right)
$$

### 3. **Upper Confidence Bound (UCB)**:
$$
UCB(x) = \mu(x) - \kappa \cdot \sigma(x)
$$

---

## 🚗 Application to Traffic Simulation

In our pipeline:

1. TraCI loads a saved simulation state.
2. A vehicle is inserted with parameters from the optimizer.
3. Simulation runs until vehicle passes the detector.
4. Compute error from real data.
5. Update the optimizer with new observation.
6. Repeat to find the best parameters.

---

## ✅ Summary

- **Bayesian Optimization** is sample-efficient.
- It uses **GPs** to model the objective and guide the search.
- In our project, it helps calibrate vehicles efficiently using **real detector data**.

---

## 📖 References

- Rasmussen & Williams, *Gaussian Processes for Machine Learning*, MIT Press (2006)
- Brochu et al., *A Tutorial on Bayesian Optimization of Expensive Cost Functions, with Application to Active User Modeling and Hierarchical Reinforcement Learning*, arXiv:1012.2599 (2010)
- Frazier, Peter I. *A tutorial on Bayesian optimization.* arXiv preprint arXiv:1807.02811 (2018)
- [Scikit-Optimize Documentation](https://scikit-optimize.github.io/)
