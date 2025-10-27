#!/usr/bin/env python3
"""
Multi-Language Templates for Incident Reports
Supports Indonesian, Mandarin, and English
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class LanguageTemplate:
    """Language template for incident reports"""
    language_code: str
    language_name: str
    title: str
    fields: Dict[str, str]
    severity_levels: Dict[str, str]
    violation_types: Dict[str, str]
    status_options: Dict[str, str]
    actions: Dict[str, str]
    notes: Dict[str, str]

class MultiLanguageTemplates:
    """Multi-language templates for incident reports"""
    
    def __init__(self):
        self.templates = {
            'id': self._get_indonesian_template(),
            'zh': self._get_mandarin_template(),
            'en': self._get_english_template()
        }
    
    def _get_indonesian_template(self) -> LanguageTemplate:
        """Indonesian template"""
        return LanguageTemplate(
            language_code='id',
            language_name='Bahasa Indonesia',
            title='Laporan Kejadian (Incident Reports)',
            fields={
                'incident_id': 'Incident ID',
                'tanggal_waktu': 'Tanggal & Waktu (Date & Time)',
                'lokasi': 'Lokasi (Location)',
                'jenis_pelanggaran': 'Jenis Pelanggaran (Type of Violation)',
                'severity': 'Severity',
                'durasi': 'Durasi (Duration)',
                'jumlah_objek': 'Jumlah Objek (Number of Objects)',
                'deskripsi': 'Deskripsi (Description)',
                'status': 'Status',
                'petugas': 'Petugas (PIC) (Officer (PIC))',
                'tindakan': 'Tindakan (Action)',
                'catatan': 'Catatan (Notes)',
                'screenshot_evidence': 'Screenshot Evidence'
            },
            severity_levels={
                'high': 'Tinggi',
                'medium': 'Sedang',
                'low': 'Rendah'
            },
            violation_types={
                'intrusion': 'Intrusi',
                'security_breach': 'Pelanggaran Keamanan',
                'unauthorized_access': 'Akses Tidak Sah',
                'suspicious_activity': 'Aktivitas Mencurigakan'
            },
            status_options={
                'resolved': 'Selesai',
                'pending': 'Menunggu',
                'investigating': 'Sedang Diselidiki',
                'escalated': 'Ditingkatkan'
            },
            actions={
                'stopped': 'Individu dihentikan oleh petugas, identitas diverifikasi, area diamankan.',
                'verified': 'Pemeriksaan keamanan berhasil diselesaikan sesuai prosedur.',
                'investigated': 'Insiden sedang diselidiki lebih lanjut oleh tim keamanan.',
                'escalated': 'Insiden telah ditingkatkan ke supervisor untuk tindakan lebih lanjut.'
            },
            notes={
                'no_damage': 'Tidak ada kerugian material, insiden dilaporkan ke supervisor.',
                'minor_damage': 'Kerugian material minimal, insiden dilaporkan ke supervisor.',
                'major_damage': 'Kerugian material signifikan, insiden dilaporkan ke supervisor dan pihak berwenang.',
                'ongoing': 'Investigasi masih berlangsung, update akan diberikan secara berkala.'
            }
        )
    
    def _get_mandarin_template(self) -> LanguageTemplate:
        """Mandarin template"""
        return LanguageTemplate(
            language_code='zh',
            language_name='中文',
            title='事件报告 (Incident Reports)',
            fields={
                'incident_id': '事件编号',
                'tanggal_waktu': '日期时间 (Date & Time)',
                'lokasi': '地点 (Location)',
                'jenis_pelanggaran': '违规类型 (Type of Violation)',
                'severity': '严重程度',
                'durasi': '持续时间 (Duration)',
                'jumlah_objek': '对象数量 (Number of Objects)',
                'deskripsi': '描述 (Description)',
                'status': '状态',
                'petugas': '负责人 (Officer)',
                'tindakan': '采取行动 (Action)',
                'catatan': '备注 (Notes)',
                'screenshot_evidence': '截图证据'
            },
            severity_levels={
                'high': '高',
                'medium': '中',
                'low': '低'
            },
            violation_types={
                'intrusion': '入侵',
                'security_breach': '安全违规',
                'unauthorized_access': '未授权访问',
                'suspicious_activity': '可疑活动'
            },
            status_options={
                'resolved': '已解决',
                'pending': '待处理',
                'investigating': '调查中',
                'escalated': '已升级'
            },
            actions={
                'stopped': '个人被安保人员制止，身份已核实，区域已安全。',
                'verified': '安全检查已按程序成功完成。',
                'investigated': '事件正在由安全团队进一步调查。',
                'escalated': '事件已升级至主管进行进一步处理。'
            },
            notes={
                'no_damage': '无物质损失，事件已报告给主管。',
                'minor_damage': '物质损失轻微，事件已报告给主管。',
                'major_damage': '物质损失重大，事件已报告给主管和相关当局。',
                'ongoing': '调查仍在进行中，将定期提供更新。'
            }
        )
    
    def _get_english_template(self) -> LanguageTemplate:
        """English template"""
        return LanguageTemplate(
            language_code='en',
            language_name='English',
            title='Incident Reports',
            fields={
                'incident_id': 'Incident ID',
                'tanggal_waktu': 'Date & Time',
                'lokasi': 'Location',
                'jenis_pelanggaran': 'Type of Violation',
                'severity': 'Severity',
                'durasi': 'Duration',
                'jumlah_objek': 'Number of Objects',
                'deskripsi': 'Description',
                'status': 'Status',
                'petugas': 'Officer (PIC)',
                'tindakan': 'Action Taken',
                'catatan': 'Notes',
                'screenshot_evidence': 'Screenshot Evidence'
            },
            severity_levels={
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low'
            },
            violation_types={
                'intrusion': 'Intrusion',
                'security_breach': 'Security Breach',
                'unauthorized_access': 'Unauthorized Access',
                'suspicious_activity': 'Suspicious Activity'
            },
            status_options={
                'resolved': 'Resolved',
                'pending': 'Pending',
                'investigating': 'Under Investigation',
                'escalated': 'Escalated'
            },
            actions={
                'stopped': 'Individual stopped by security officer, identity verified, area secured.',
                'verified': 'Security check completed successfully according to procedure.',
                'investigated': 'Incident is being further investigated by security team.',
                'escalated': 'Incident has been escalated to supervisor for further action.'
            },
            notes={
                'no_damage': 'No material damage, incident reported to supervisor.',
                'minor_damage': 'Minor material damage, incident reported to supervisor.',
                'major_damage': 'Significant material damage, incident reported to supervisor and authorities.',
                'ongoing': 'Investigation ongoing, updates will be provided periodically.'
            }
        )
    
    def get_template(self, language_code: str) -> LanguageTemplate:
        """Get template for specific language"""
        return self.templates.get(language_code, self.templates['en'])
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages"""
        return {code: template.language_name for code, template in self.templates.items()}
    
    def translate_incident_data(self, incident_data: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate incident data to target language"""
        template = self.get_template(target_language)
        
        # Translate severity
        severity = incident_data.get('severity', 'medium').lower()
        translated_severity = template.severity_levels.get(severity, severity)
        
        # Translate violation type
        violation_type = incident_data.get('jenis_pelanggaran', 'intrusion').lower()
        translated_violation = template.violation_types.get(violation_type, violation_type)
        
        # Translate status
        status = incident_data.get('status', 'resolved').lower()
        translated_status = template.status_options.get(status, status)
        
        # Translate action based on score
        score = incident_data.get('score', 0.9)
        if score < 0.7:
            action_key = 'stopped'
        elif score < 0.9:
            action_key = 'investigated'
        else:
            action_key = 'verified'
        translated_action = template.actions.get(action_key, template.actions['verified'])
        
        # Translate notes
        notes_key = 'no_damage'  # Default
        if incident_data.get('severity') == 'high':
            notes_key = 'major_damage'
        elif incident_data.get('severity') == 'medium':
            notes_key = 'minor_damage'
        translated_notes = template.notes.get(notes_key, template.notes['no_damage'])
        
        # Generate translated description
        if target_language == 'id':
            description = f"Seorang individu memasuki area {incident_data.get('lokasi', 'Loading Dock - Kamera 2')} tanpa otorisasi melalui pintu samping"
        elif target_language == 'zh':
            description = f"一名个人未经授权通过侧门进入{incident_data.get('lokasi', 'Loading Dock - Kamera 2')}区域"
        else:  # English
            description = f"An individual entered the {incident_data.get('lokasi', 'Loading Dock - Kamera 2')} area without authorization through the side door"
        
        return {
            'incident_id': incident_data.get('incident_id', ''),
            'tanggal_waktu': incident_data.get('tanggal_waktu', ''),
            'lokasi': incident_data.get('lokasi', ''),
            'jenis_pelanggaran': translated_violation,
            'severity': translated_severity,
            'durasi': incident_data.get('durasi', ''),
            'jumlah_objek': incident_data.get('jumlah_objek', ''),
            'deskripsi': description,
            'status': translated_status,
            'petugas': incident_data.get('petugas', ''),
            'tindakan': translated_action,
            'catatan': translated_notes,
            'screenshot_path': incident_data.get('screenshot_path', '')
        }
