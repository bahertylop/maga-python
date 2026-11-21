"""
**Задача 38 (FFT и обработка сигналов).** Дан сигнал — сумма двух синусоид с шумом (например, сезонные колебания продаж):
```python
t = np.linspace(0, 1, 1000, endpoint=False)
signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 12 * t)
noisy = signal + np.random.default_rng(42).normal(0, 0.3, 1000)
```
Выполните:
- `np.fft.fft(noisy)`;
- `np.fft.fftfreq(len(noisy), d=1/1000)`;
- `amplitudes = np.abs(fft) / len(noisy) * 2`;
- топ-2 частоты через `np.argsort(amplitudes)[-2:]`.

Отфильтруйте шум: обнулите частоты выше 20 Гц и `np.fft.ifft`. Сравните ошибку до/после. **Что продемонстрировать:** FFT, выделение частот, фильтрацию. **Вопросы:** что такое FFT; почему степени двойки эффективнее; как амплитуда связана с коэффициентом; как FFT применяется к анализу сезонности продаж в автосалоне.
"""
import numpy as np

t = np.linspace(0, 1, 1000, endpoint=False)
signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 12 * t)
noisy = signal + np.random.default_rng(42).normal(0, 0.3, 1000)

fft = np.fft.fft(noisy)
freqs = np.fft.fftfreq(len(noisy), d=1 / 1000)
amplitudes = np.abs(fft) / len(noisy) * 2
# Спектр вещественного сигнала зеркален: берём ТОЛЬКО положительные частоты. Иначе в
# argsort(amplitudes)[-2:] попадут +5 и -5 Гц (одна и та же составляющая).
half = len(noisy) // 2
top2 = np.argsort(amplitudes[1:half])[-2:] + 1
print("главные частоты, Гц:", np.sort(freqs[top2]), "| амплитуды:", amplitudes[top2].round(3))

fft_f = fft.copy()
fft_f[np.abs(freqs) > 20] = 0                  # обнуляем всё выше 20 Гц (и +, и -)
filtered = np.fft.ifft(fft_f).real
mse = lambda x: float(np.mean((x - signal) ** 2))
print(f"MSE до фильтра: {mse(noisy):.4f} | после: {mse(filtered):.4f}")
# FFT (быстрое преобразование Фурье) раскладывает сигнал на сумму синусоид и показывает,
# какие частоты в нём есть; DFT - O(n²), FFT - O(n log n); эффективнее всего для длин-степеней двойки
# (алгоритм делит задачу пополам), но NumPy справляется и с другими. Амплитуда синусоиды =
# 2*|X_k|/N (множитель 2 - из-за зеркальной отрицательной частоты). Для автосалона: FFT
# продаж по дням находит периоды сезонности (пик на 1/7 дня-1 -> недельный цикл, 1/365 -> годовой).
daily = 50 + 10 * np.sin(2 * np.pi * np.arange(364) / 7) + np.random.default_rng(1).normal(0, 2, 364)
f = np.fft.rfftfreq(364, d=1)
print("период главной сезонности, дней:", round(1 / f[1:][np.argmax(np.abs(np.fft.rfft(daily - daily.mean()))[1:])], 2))
