use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString};

/// Heurística Bitwise (Rust Speed) - ORIGINAL
#[pyfunction]
fn calc_p_rust(texto: &str) -> PyResult<i32> {
    let t = texto.to_lowercase();
    let mut p_al = 0;
    
    // Keywords (Hardcoded for raw speed)
    if t.contains("fuego") { p_al += 50; }
    if t.contains("critico") { p_al += 40; }
    if t.contains("urgente") { p_al += 35; }
    if t.contains("falla") { p_al += 30; }
    if t.contains("peligro") { p_al += 45; }
    
    if p_al >= 30 {
        Ok(100) // PRIORIDAD_ALTA
    } else if p_al >= 15 {
        Ok(50)  // PRIORIDAD_MEDIA
    } else {
        Ok(10)  // PRIORIDAD_BAJA
    }
}

/// NUEVO: Actualiza Q-value usando la fórmula de Q-Learning
/// Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
#[pyfunction]
fn update_q_value(
    current_q: f64,
    reward: f64,
    next_max_q: f64,
    learning_rate: f64,
    discount: f64,
) -> PyResult<f64> {
    let new_q = current_q + learning_rate * (reward + discount * next_max_q - current_q);
    Ok(new_q)
}

/// NUEVO: Multiplicación rápida de matrices para tensores
#[pyfunction]
fn tensor_multiply(a: Vec<Vec<f64>>, b: Vec<Vec<f64>>) -> PyResult<Vec<Vec<f64>>> {
    if a.is_empty() || b.is_empty() {
        return Ok(vec![]);
    }
    
    let rows_a = a.len();
    let cols_a = a[0].len();
    let rows_b = b.len();
    let cols_b = b[0].len();
    
    if cols_a != rows_b {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Matrix dimensions don't match for multiplication"
        ));
    }
    
    let mut result = vec![vec![0.0; cols_b]; rows_a];
    
    for i in 0..rows_a {
        for j in 0..cols_b {
            for k in 0..cols_a {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    
    Ok(result)
}

/// NUEVO: Calcula recompensa acumulada con descuento (para RL)
#[pyfunction]
fn calculate_discounted_reward(rewards: Vec<f64>, gamma: f64) -> PyResult<Vec<f64>> {
    let mut discounted = vec![0.0; rewards.len()];
    let mut running_add = 0.0;
    
    for i in (0..rewards.len()).rev() {
        running_add = running_add * gamma + rewards[i];
        discounted[i] = running_add;
    }
    
    Ok(discounted)
}

/// NUEVO: Softmax para selección de acciones
#[pyfunction]
fn softmax(values: Vec<f64>, temperature: f64) -> PyResult<Vec<f64>> {
    let max_val = values.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    
    let exp_values: Vec<f64> = values
        .iter()
        .map(|&v| ((v - max_val) / temperature).exp())
        .collect();
    
    let sum: f64 = exp_values.iter().sum();
    
    let probabilities: Vec<f64> = exp_values
        .iter()
        .map(|&v| v / sum)
        .collect();
    
    Ok(probabilities)
}

/// NUEVO: Epsilon-greedy selection
#[pyfunction]
fn epsilon_greedy_select(q_values: Vec<f64>, epsilon: f64, random_val: f64) -> PyResult<usize> {
    if random_val < epsilon {
        // Exploración: acción aleatoria
        Ok((random_val * q_values.len() as f64) as usize)
    } else {
        // Explotación: mejor acción
        let max_idx = q_values
            .iter()
            .enumerate()
            .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap())
            .map(|(idx, _)| idx)
            .unwrap_or(0);
        Ok(max_idx)
    }
}

/// Modulo Python
#[pymodule]
fn k_ia(_py: Python, m: &PyModule) -> PyResult<()> {
    // Función original
    m.add_function(wrap_pyfunction!(calc_p_rust, m)?)?;
    
    // Nuevas funciones de RL
    m.add_function(wrap_pyfunction!(update_q_value, m)?)?;
    m.add_function(wrap_pyfunction!(tensor_multiply, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_discounted_reward, m)?)?;
    m.add_function(wrap_pyfunction!(softmax, m)?)?;
    m.add_function(wrap_pyfunction!(epsilon_greedy_select, m)?)?;
    
    Ok(())
}
