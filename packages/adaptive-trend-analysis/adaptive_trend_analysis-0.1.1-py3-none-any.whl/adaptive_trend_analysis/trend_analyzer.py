import numpy as np
import pandas as pd

class GradientAdaptiveSmoothing:
    def __init__(self, df: pd.DataFrame, value_col: str):
        self.df = df.copy()
        self.value_col = value_col
        self.init_columns()
    
    def init_columns(self):
        cols = ["Gradient", "Abs_Gradient", "Std_Dev", "IQR", "Normalized_Gradient",
                "Trend_Sensitivity", "Adaptive_Smoothing", "Adaptive_Trend", "Level", "Trend", "K", "L", "n"]
        for col in cols:
            self.df[col] = 0.0
    
    def compute_trend(self):
        for i in range(1, len(self.df)):
            self.df.loc[i, 'Abs_Gradient'] = abs(self.df.loc[i, self.value_col] - self.df.loc[i-1, self.value_col])
            self.df.loc[i, 'Std_Dev'] = self.df.loc[:i, 'Abs_Gradient'].std(ddof=1) if i > 1 else 0
            self.df.loc[i, 'IQR'] = np.percentile(self.df.loc[:i, 'Abs_Gradient'], 75) - np.percentile(self.df.loc[:i, 'Abs_Gradient'], 25)
            
            if self.df.loc[i, 'Std_Dev'] == 0:
                self.df.loc[i, 'Normalized_Gradient'] = 0
            else:
                self.df.loc[i, 'Normalized_Gradient'] = self.df.loc[i, 'Abs_Gradient'] / self.df.loc[i, 'Std_Dev']
            
            self.df.loc[i, 'Trend_Sensitivity'] = np.exp(-self.df.loc[i, 'Normalized_Gradient'])
            
            abs_diff = abs(self.df.loc[i, 'Abs_Gradient'] - self.df.loc[i-1, 'Abs_Gradient']) if i > 1 else 0
            max_abs = max(abs(self.df.loc[i, 'Abs_Gradient']), abs(self.df.loc[i-1, 'Abs_Gradient']), 0.0001)
            self.df.loc[i, 'Adaptive_Smoothing'] = 1 - (self.df.loc[i, 'Trend_Sensitivity'] * (1 - abs_diff / max_abs))
            
            self.df.loc[i, 'Adaptive_Trend'] = self.df.loc[i, 'Trend_Sensitivity'] * self.df.loc[i, 'Normalized_Gradient']
            
            self.df.loc[i, 'Level'] = self.df.loc[i-1, self.value_col]
            self.df.loc[i, 'Trend'] = self.df.loc[i-1, self.value_col] - self.df.loc[i-2, self.value_col] if i > 1 else 0
            
            if i > 1:
                self.df.loc[i, 'K'] = self.df.loc[i, 'Adaptive_Smoothing'] * self.df.loc[i, self.value_col] + \
                                      (1 - self.df.loc[i, 'Adaptive_Smoothing']) * (self.df.loc[i-1, 'K'] + self.df.loc[i-1, 'L'])
                self.df.loc[i, 'L'] = self.df.loc[i, 'Adaptive_Trend'] * (self.df.loc[i, 'K'] - self.df.loc[i-1, 'K']) + \
                                      (1 - self.df.loc[i, 'Adaptive_Trend']) * self.df.loc[i-1, 'L']
                self.df.loc[i, 'n'] = self.df.loc[i-1, 'K'] + self.df.loc[i-1, 'L']
    
    def detect_seasonality(self, condition=True):
        if condition:
            self.df['Final_Prediction'] = self.df['K'] + self.df['Adaptive_Smoothing'] / 2
    
    def get_results(self):
        return self.df
