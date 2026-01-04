import os
import pandas as pd
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    roc_curve, auc, precision_recall_curve,
    roc_auc_score, f1_score, accuracy_score,
    precision_score, recall_score
)
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = "data"
MODEL_DIR = "model"
RESULTS_DIR = "results"
TEST_PATH = os.path.join(DATA_DIR, "test_llm_v1.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "deepsea_model_llm_v1.pkl")

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_test():
    test_df = pd.read_csv(TEST_PATH)
    return test_df

def comprehensive_evaluation(y_true, y_pred, y_proba, test_df=None):
    """Generate comprehensive evaluation metrics and visualizations"""
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE MODEL EVALUATION")
    print("=" * 60)
    
    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, y_proba)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    
    print(f"Overall Performance:")
    print(f"  Accuracy:  {accuracy:.3f}")
    print(f"  F1-Score:  {f1:.3f}")
    print(f"  ROC-AUC:   {roc_auc:.3f}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall:    {recall:.3f}")
    
    # Classification report
    print("\n📋 Detailed Classification Report:")
    report_dict = classification_report(y_true, y_pred, output_dict=True, digits=3)
    print(classification_report(y_true, y_pred, digits=3))
    
    # Save overall metrics to CSV
    overall_metrics = pd.DataFrame([{
        'metric': 'Overall',
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'roc_auc': roc_auc,
        'n_samples': len(y_true)
    }])
    overall_metrics.to_csv(os.path.join(RESULTS_DIR, 'overall_metrics.csv'), index=False)
    print(f"Overall metrics saved to {os.path.join(RESULTS_DIR, 'overall_metrics.csv')}")
    
    # Save per-class metrics to CSV
    per_class_metrics = []
    for class_label in [0, 1]:
        class_name = 'Task-Oriented' if class_label == 0 else 'Emotionally Dependent'
        if str(class_label) in report_dict:
            metrics = report_dict[str(class_label)]
            per_class_metrics.append({
                'class': class_label,
                'class_name': class_name,
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1_score': metrics['f1-score'],
                'support': metrics['support']
            })
    
    # Add macro and weighted averages
    if 'macro avg' in report_dict:
        per_class_metrics.append({
            'class': 'macro_avg',
            'class_name': 'Macro Average',
            'precision': report_dict['macro avg']['precision'],
            'recall': report_dict['macro avg']['recall'],
            'f1_score': report_dict['macro avg']['f1-score'],
            'support': report_dict['macro avg']['support']
        })
    if 'weighted avg' in report_dict:
        per_class_metrics.append({
            'class': 'weighted_avg',
            'class_name': 'Weighted Average',
            'precision': report_dict['weighted avg']['precision'],
            'recall': report_dict['weighted avg']['recall'],
            'f1_score': report_dict['weighted avg']['f1-score'],
            'support': report_dict['weighted avg']['support']
        })
    
    per_class_df = pd.DataFrame(per_class_metrics)
    per_class_df.to_csv(os.path.join(RESULTS_DIR, 'per_class_metrics.csv'), index=False)
    print(f"Per-class metrics saved to {os.path.join(RESULTS_DIR, 'per_class_metrics.csv')}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Task-Oriented', 'Emotionally Dependent'],
                yticklabels=['Task-Oriented', 'Emotionally Dependent'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrix.png'), dpi=150)
    print(f"\nConfusion matrix saved to {os.path.join(RESULTS_DIR, 'confusion_matrix.png')}")
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.3f})', linewidth=2)
    plt.plot([0, 1], [0, 1], 'k--', label='Random classifier')
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'roc_curve.png'), dpi=150)
    print(f"ROC curve saved to {os.path.join(RESULTS_DIR, 'roc_curve.png')}")
    
    # Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true, y_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, linewidth=2)
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curve', fontsize=14)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'pr_curve.png'), dpi=150)
    print(f"Precision-Recall curve saved to {os.path.join(RESULTS_DIR, 'pr_curve.png')}")
    
    # Performance by difficulty (if available)
    difficulty_perf = []
    if test_df is not None and 'difficulty' in test_df.columns:
        print("\n📈 Performance by Difficulty:")
        for difficulty in ['easy', 'hard']:
            mask = test_df['difficulty'] == difficulty
            if mask.sum() > 0:
                diff_accuracy = accuracy_score(y_true[mask], y_pred[mask])
                diff_f1 = f1_score(y_true[mask], y_pred[mask])
                diff_precision = precision_score(y_true[mask], y_pred[mask], zero_division=0)
                diff_recall = recall_score(y_true[mask], y_pred[mask], zero_division=0)
                print(f"  {difficulty.capitalize()}: Accuracy={diff_accuracy:.3f}, F1={diff_f1:.3f} (n={mask.sum()})")
                difficulty_perf.append({
                    'difficulty': difficulty,
                    'accuracy': diff_accuracy,
                    'precision': diff_precision,
                    'recall': diff_recall,
                    'f1_score': diff_f1,
                    'n_samples': mask.sum()
                })
        
        if difficulty_perf:
            difficulty_df = pd.DataFrame(difficulty_perf)
            difficulty_df.to_csv(os.path.join(RESULTS_DIR, 'performance_by_difficulty.csv'), index=False)
            print(f" Performance by difficulty saved to {os.path.join(RESULTS_DIR, 'performance_by_difficulty.csv')}")
    
    # Performance by template_id (if available)
    template_perf = []
    if test_df is not None and 'template_id' in test_df.columns:
        print("Performance by Template:")
        for template_id in test_df['template_id'].unique():
            mask = test_df['template_id'] == template_id
            if mask.sum() > 0:
                temp_accuracy = accuracy_score(y_true[mask], y_pred[mask])
                temp_f1 = f1_score(y_true[mask], y_pred[mask])
                temp_precision = precision_score(y_true[mask], y_pred[mask], zero_division=0)
                temp_recall = recall_score(y_true[mask], y_pred[mask], zero_division=0)
                template_perf.append({
                    'template_id': template_id,
                    'accuracy': temp_accuracy,
                    'precision': temp_precision,
                    'recall': temp_recall,
                    'f1_score': temp_f1,
                    'n_samples': mask.sum()
                })
        
        if template_perf:
            perf_df = pd.DataFrame(template_perf).sort_values('accuracy', ascending=False)
            print(perf_df.to_string(index=False))
            perf_df.to_csv(os.path.join(RESULTS_DIR, 'performance_by_template.csv'), index=False)
            print(f"Performance by template saved to {os.path.join(RESULTS_DIR, 'performance_by_template.csv')}")
    
    # Save confusion matrix to CSV
    cm_df = pd.DataFrame(cm, 
                         index=['True: Task-Oriented', 'True: Emotionally Dependent'],
                         columns=['Pred: Task-Oriented', 'Pred: Emotionally Dependent'])
    cm_df.to_csv(os.path.join(RESULTS_DIR, 'confusion_matrix.csv'))
    print(f"Confusion matrix saved to {os.path.join(RESULTS_DIR, 'confusion_matrix.csv')}")
    
    # Save predictions with probabilities (optional detailed results)
    if test_df is not None:
        predictions_df = test_df[['id', 'text', 'label']].copy() if 'id' in test_df.columns else test_df[['text', 'label']].copy()
        predictions_df['predicted_label'] = y_pred
        predictions_df['predicted_probability'] = y_proba
        predictions_df['correct'] = (y_true == y_pred).astype(int)
        
        # Add difficulty and template_id if available
        if 'difficulty' in test_df.columns:
            predictions_df['difficulty'] = test_df['difficulty'].values
        if 'template_id' in test_df.columns:
            predictions_df['template_id'] = test_df['template_id'].values
        
        predictions_df.to_csv(os.path.join(RESULTS_DIR, 'predictions.csv'), index=False)
        print(f"Detailed predictions saved to {os.path.join(RESULTS_DIR, 'predictions.csv')}")
    
    return {
        'accuracy': accuracy,
        'f1_score': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm
    }

def main():
    test_df = load_test()
    model = joblib.load(MODEL_PATH)

    X_test = test_df["text"].astype(str)
    y_test = test_df["label"].astype(int)

    # Get predictions and probabilities
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]  # Probability of class 1
    
    # Comprehensive evaluation
    comprehensive_evaluation(y_test, y_pred, y_proba, test_df)
    
    print("\n" + "=" * 60)
    print("Evaluation complete!")
    print(f"Check the '{RESULTS_DIR}/' directory for:")
    print("   - Visualizations (PNG files)")
    print("   - Evaluation metrics (CSV files)")
    print("=" * 60)

if __name__ == "__main__":
    main()
