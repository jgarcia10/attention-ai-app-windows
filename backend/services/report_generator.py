"""
Report generator for attention analysis
"""
import json
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from PIL import Image
import cv2


class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set matplotlib to use Spanish locale
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_attention_report(self, recording_id: str, recording_info: Dict[str, Any], 
                                attention_data: Dict[str, Any], sample_frames: List[np.ndarray] = None) -> str:
        """
        Generate a comprehensive attention analysis report
        
        Args:
            recording_id: Recording identifier
            recording_info: Information about the recording
            attention_data: Attention tracking data
            sample_frames: Sample frames from the recording
            
        Returns:
            Path to the generated PDF report
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"reporte_atencion_{recording_id}_{timestamp}.pdf"
        report_path = self.output_dir / report_filename
        
        # Create PDF report
        with PdfPages(report_path) as pdf:
            # Page 1: Cover page
            self._create_cover_page(pdf, recording_id, recording_info)
            
            # Page 2: Executive summary
            self._create_executive_summary(pdf, attention_data)
            
            # Page 3: Attention timeline plot
            self._create_attention_timeline(pdf, attention_data)
            
            # Page 4: Statistics and analysis
            self._create_statistics_page(pdf, attention_data)
            
            # Page 5: Sample frames (if available)
            if sample_frames:
                self._create_sample_frames_page(pdf, sample_frames)
        
        print(f"Generated attention report: {report_path}")
        return str(report_path)
    
    def _create_cover_page(self, pdf: PdfPages, recording_id: str, recording_info: Dict[str, Any]):
        """Create the cover page of the report"""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.9, 'REPORTE DE ANÁLISIS DE ATENCIÓN', 
                ha='center', va='center', fontsize=24, fontweight='bold', color='#1e40af')
        
        # Subtitle
        ax.text(0.5, 0.85, 'Sistema de Monitoreo de Atención en Conferencias', 
                ha='center', va='center', fontsize=14, color='#64748b')
        
        # Recording information
        y_pos = 0.75
        ax.text(0.1, y_pos, 'INFORMACIÓN DE LA GRABACIÓN:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        y_pos -= 0.05
        ax.text(0.1, y_pos, f'ID de Grabación: {recording_id}', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.04
        if 'custom_name' in recording_info:
            ax.text(0.1, y_pos, f'Nombre de la Conferencia: {recording_info["custom_name"]}', 
                    ha='left', va='center', fontsize=12)
            y_pos -= 0.04
        
        ax.text(0.1, y_pos, f'Duración: {recording_info.get("duration", 0):.2f} segundos', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.04
        ax.text(0.1, y_pos, f'Resolución: {recording_info.get("width", 0)}x{recording_info.get("height", 0)}', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.04
        ax.text(0.1, y_pos, f'FPS: {recording_info.get("fps", 0)}', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.04
        ax.text(0.1, y_pos, f'Total de Frames: {recording_info.get("frame_count", 0)}', 
                ha='left', va='center', fontsize=12)
        
        # Date
        current_date = datetime.now().strftime("%d de %B de %Y")
        ax.text(0.5, 0.2, f'Generado el {current_date}', 
                ha='center', va='center', fontsize=12, style='italic', color='#64748b')
        
        # Footer
        ax.text(0.5, 0.1, 'Sistema de Análisis de Atención - GotoCloud', 
                ha='center', va='center', fontsize=10, color='#64748b')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_executive_summary(self, pdf: PdfPages, attention_data: Dict[str, Any]):
        """Create executive summary page"""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'RESUMEN EJECUTIVO', 
                ha='center', va='center', fontsize=20, fontweight='bold', color='#1e40af')
        
        summary_stats = attention_data.get('summary_statistics', {})
        
        # Key metrics
        y_pos = 0.85
        ax.text(0.1, y_pos, 'MÉTRICAS PRINCIPALES:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        y_pos -= 0.08
        avg_attention = summary_stats.get('average_attention_percentage', 0)
        ax.text(0.1, y_pos, f'• Nivel Promedio de Atención: {avg_attention:.1f}%', 
                ha='left', va='center', fontsize=14, fontweight='bold', 
                color='#059669' if avg_attention >= 60 else '#dc2626' if avg_attention < 40 else '#d97706')
        
        y_pos -= 0.06
        max_attention = summary_stats.get('max_attention_percentage', 0)
        ax.text(0.1, y_pos, f'• Pico Máximo de Atención: {max_attention:.1f}%', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        min_attention = summary_stats.get('min_attention_percentage', 0)
        ax.text(0.1, y_pos, f'• Nivel Mínimo de Atención: {min_attention:.1f}%', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        avg_people = summary_stats.get('average_total_people', 0)
        ax.text(0.1, y_pos, f'• Promedio de Personas Detectadas: {avg_people:.1f}', 
                ha='left', va='center', fontsize=12)
        
        # Attention levels
        y_pos -= 0.08
        ax.text(0.1, y_pos, 'DISTRIBUCIÓN DE NIVELES DE ATENCIÓN:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        y_pos -= 0.06
        high_pct = summary_stats.get('high_attention_percentage', 0)
        ax.text(0.1, y_pos, f'• Alta Atención (≥70%): {high_pct:.1f}% del tiempo', 
                ha='left', va='center', fontsize=12, color='#059669')
        
        y_pos -= 0.05
        medium_pct = summary_stats.get('medium_attention_percentage', 0)
        ax.text(0.1, y_pos, f'• Atención Media (30-70%): {medium_pct:.1f}% del tiempo', 
                ha='left', va='center', fontsize=12, color='#d97706')
        
        y_pos -= 0.05
        low_pct = summary_stats.get('low_attention_percentage', 0)
        ax.text(0.1, y_pos, f'• Baja Atención (<30%): {low_pct:.1f}% del tiempo', 
                ha='left', va='center', fontsize=12, color='#dc2626')
        
        # Recommendations
        y_pos -= 0.08
        ax.text(0.1, y_pos, 'RECOMENDACIONES:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        recommendations = self._generate_recommendations(summary_stats)
        for i, rec in enumerate(recommendations):
            y_pos -= 0.05
            ax.text(0.1, y_pos, f'• {rec}', 
                    ha='left', va='center', fontsize=11, wrap=True)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_attention_timeline(self, pdf: PdfPages, attention_data: Dict[str, Any]):
        """Create attention timeline plot"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 11))
        
        tracking_data = attention_data.get('tracking_data', [])
        if not tracking_data:
            ax1.text(0.5, 0.5, 'No hay datos de seguimiento disponibles', 
                    ha='center', va='center', fontsize=14)
            ax2.text(0.5, 0.5, 'No hay datos de seguimiento disponibles', 
                    ha='center', va='center', fontsize=14)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            return
        
        # Extract data
        times = [point['relative_time'] / 60.0 for point in tracking_data]  # Convert to minutes
        attention_pct = [point['attention_percentage'] for point in tracking_data]
        total_people = [point['total_people'] for point in tracking_data]
        
        # Plot 1: Attention percentage over time
        ax1.plot(times, attention_pct, color='#059669', linewidth=2, label='Atención')
        ax1.fill_between(times, attention_pct, alpha=0.3, color='#059669')
        ax1.set_xlabel('Tiempo (minutos)', fontsize=12)
        ax1.set_ylabel('Porcentaje de Atención (%)', fontsize=12)
        ax1.set_title('Evolución del Nivel de Atención Durante la Conferencia', 
                     fontsize=14, fontweight='bold', color='#1e40af')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        ax1.legend()
        
        # Add attention level zones
        ax1.axhspan(70, 100, alpha=0.1, color='green', label='Alta Atención')
        ax1.axhspan(30, 70, alpha=0.1, color='orange', label='Atención Media')
        ax1.axhspan(0, 30, alpha=0.1, color='red', label='Baja Atención')
        
        # Plot 2: Number of people over time
        ax2.plot(times, total_people, color='#1e40af', linewidth=2, marker='o', markersize=3)
        ax2.set_xlabel('Tiempo (minutos)', fontsize=12)
        ax2.set_ylabel('Número de Personas', fontsize=12)
        ax2.set_title('Número de Personas Detectadas Durante la Conferencia', 
                     fontsize=14, fontweight='bold', color='#1e40af')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, max(total_people) + 1 if total_people else 1)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_statistics_page(self, pdf: PdfPages, attention_data: Dict[str, Any]):
        """Create detailed statistics page"""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'ANÁLISIS ESTADÍSTICO DETALLADO', 
                ha='center', va='center', fontsize=20, fontweight='bold', color='#1e40af')
        
        summary_stats = attention_data.get('summary_statistics', {})
        tracking_data = attention_data.get('tracking_data', [])
        
        # General statistics
        y_pos = 0.85
        ax.text(0.1, y_pos, 'ESTADÍSTICAS GENERALES:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        y_pos -= 0.06
        duration = attention_data.get('total_duration', 0)
        ax.text(0.1, y_pos, f'• Duración Total: {duration:.2f} segundos ({duration/60:.1f} minutos)', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        total_frames = len(tracking_data)
        ax.text(0.1, y_pos, f'• Total de Frames Analizados: {total_frames}', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        fps = total_frames / duration if duration > 0 else 0
        ax.text(0.1, y_pos, f'• FPS Promedio: {fps:.2f}', 
                ha='left', va='center', fontsize=12)
        
        # Attention statistics
        y_pos -= 0.08
        ax.text(0.1, y_pos, 'ESTADÍSTICAS DE ATENCIÓN:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        y_pos -= 0.06
        avg_attention = summary_stats.get('average_attention_percentage', 0)
        ax.text(0.1, y_pos, f'• Atención Promedio: {avg_attention:.2f}%', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        avg_distracted = summary_stats.get('average_distracted_percentage', 0)
        ax.text(0.1, y_pos, f'• Distracción Promedio: {avg_distracted:.2f}%', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        avg_no_face = summary_stats.get('average_no_face_percentage', 0)
        ax.text(0.1, y_pos, f'• Sin Rostro Detectado: {avg_no_face:.2f}%', 
                ha='left', va='center', fontsize=12)
        
        # Time analysis
        y_pos -= 0.08
        ax.text(0.1, y_pos, 'ANÁLISIS TEMPORAL:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        y_pos -= 0.06
        attention_time = summary_stats.get('total_attention_time_seconds', 0)
        ax.text(0.1, y_pos, f'• Tiempo Total de Alta Atención: {attention_time:.2f} segundos', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        distracted_time = summary_stats.get('total_distracted_time_seconds', 0)
        ax.text(0.1, y_pos, f'• Tiempo Total de Distracción: {distracted_time:.2f} segundos', 
                ha='left', va='center', fontsize=12)
        
        y_pos -= 0.05
        no_face_time = summary_stats.get('total_no_face_time_seconds', 0)
        ax.text(0.1, y_pos, f'• Tiempo Sin Rostro Detectado: {no_face_time:.2f} segundos', 
                ha='left', va='center', fontsize=12)
        
        # Performance indicators
        y_pos -= 0.08
        ax.text(0.1, y_pos, 'INDICADORES DE RENDIMIENTO:', 
                ha='left', va='center', fontsize=16, fontweight='bold', color='#1e40af')
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(summary_stats)
        y_pos -= 0.06
        ax.text(0.1, y_pos, f'• Puntuación General de Atención: {performance_score:.1f}/100', 
                ha='left', va='center', fontsize=14, fontweight='bold', 
                color='#059669' if performance_score >= 70 else '#dc2626' if performance_score < 50 else '#d97706')
        
        y_pos -= 0.05
        if performance_score >= 70:
            ax.text(0.1, y_pos, '  → Excelente nivel de atención de la audiencia', 
                    ha='left', va='center', fontsize=11, color='#059669')
        elif performance_score >= 50:
            ax.text(0.1, y_pos, '  → Nivel moderado de atención, hay margen de mejora', 
                    ha='left', va='center', fontsize=11, color='#d97706')
        else:
            ax.text(0.1, y_pos, '  → Nivel bajo de atención, se recomienda revisar la presentación', 
                    ha='left', va='center', fontsize=11, color='#dc2626')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_sample_frames_page(self, pdf: PdfPages, sample_frames: List[np.ndarray]):
        """Create page with sample frames from the recording"""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'MUESTRAS DE LA GRABACIÓN', 
                ha='center', va='center', fontsize=20, fontweight='bold', color='#1e40af')
        
        # Display sample frames
        if sample_frames:
            # Take up to 4 sample frames
            num_frames = min(4, len(sample_frames))
            cols = 2
            rows = (num_frames + 1) // 2
            
            frame_width = 0.4
            frame_height = 0.3
            
            for i in range(num_frames):
                row = i // cols
                col = i % cols
                
                x = 0.1 + col * 0.5
                y = 0.7 - row * 0.35
                
                # Convert BGR to RGB for matplotlib
                frame_rgb = cv2.cvtColor(sample_frames[i], cv2.COLOR_BGR2RGB)
                
                # Create inset axes for the frame
                ax_inset = fig.add_axes([x, y, frame_width, frame_height])
                ax_inset.imshow(frame_rgb)
                ax_inset.set_title(f'Frame {i+1}', fontsize=10)
                ax_inset.axis('off')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _generate_recommendations(self, summary_stats: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on statistics"""
        recommendations = []
        
        avg_attention = summary_stats.get('average_attention_percentage', 0)
        high_attention_pct = summary_stats.get('high_attention_percentage', 0)
        low_attention_pct = summary_stats.get('low_attention_percentage', 0)
        
        if avg_attention < 40:
            recommendations.append("Considerar hacer la presentación más interactiva para aumentar el engagement")
            recommendations.append("Incluir más elementos visuales y dinámicos en la presentación")
        elif avg_attention < 60:
            recommendations.append("Mejorar la estructura de la presentación para mantener mejor la atención")
            recommendations.append("Incluir pausas para preguntas y participación de la audiencia")
        else:
            recommendations.append("Excelente nivel de atención mantenido durante la presentación")
        
        if high_attention_pct < 30:
            recommendations.append("Identificar los momentos de mayor atención para replicar esas técnicas")
        
        if low_attention_pct > 40:
            recommendations.append("Revisar las secciones con menor atención para mejorar el contenido")
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def _calculate_performance_score(self, summary_stats: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        avg_attention = summary_stats.get('average_attention_percentage', 0)
        high_attention_pct = summary_stats.get('high_attention_percentage', 0)
        low_attention_pct = summary_stats.get('low_attention_percentage', 0)
        
        # Weighted score calculation
        score = (avg_attention * 0.5) + (high_attention_pct * 0.3) + ((100 - low_attention_pct) * 0.2)
        return min(100, max(0, score))
