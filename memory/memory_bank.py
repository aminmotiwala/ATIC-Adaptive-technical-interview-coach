"""
Memory Bank Implementation  
Author: Amin Motiwala

This module implements the long-term memory system for ATIC, storing user profiles,
session history, performance metrics, and learning adaptations for continuous improvement.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sqlite3
from pathlib import Path


class MemoryBank:
    """
    Long-term memory storage system for ATIC.
    
    This class implements:
    - User profile storage and management
    - Session history and performance tracking
    - Learning adaptation data persistence
    - Query and analysis capabilities
    - Data export and backup functionality
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the Memory Bank with persistent storage.
        
        Args:
            db_path: Path to SQLite database file (creates if doesn't exist)
        """
        if db_path is None:
            # Create default database in memory directory
            db_dir = Path(__file__).parent / 'data'
            db_dir.mkdir(exist_ok=True)
            db_path = db_dir / 'atic_memory.db'
        
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize SQLite database with required tables."""
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        
        cursor = self.connection.cursor()
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                experience_years INTEGER,
                technical_field TEXT,
                current_role TEXT,
                skill_levels TEXT,  -- JSON string
                learning_preferences TEXT,  -- JSON string
                profile_data TEXT  -- JSON string for full profile
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT,
                target_company TEXT,
                target_role TEXT,
                difficulty_level TEXT,
                session_data TEXT,  -- JSON string for full session data
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                category TEXT,  -- e.g., 'problem_solving', 'communication'
                metric_name TEXT,
                metric_value REAL,
                additional_data TEXT,  -- JSON string for extra context
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Learning adaptations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_adaptations (
                adaptation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                adaptation_type TEXT,  -- e.g., 'difficulty_adjustment', 'focus_area_change'
                previous_value TEXT,
                new_value TEXT,
                reason TEXT,
                effectiveness_score REAL,
                adaptation_data TEXT,  -- JSON string
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id),
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Question performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_performance (
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                question_id TEXT,
                question_type TEXT,
                question_difficulty TEXT,
                topic_area TEXT,
                response_time_seconds INTEGER,
                accuracy_score REAL,
                completeness_score REAL,
                communication_score REAL,
                question_data TEXT,  -- JSON string
                response_data TEXT,  -- JSON string
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        self.connection.commit()
        print(f"💾 Memory Bank initialized with database: {self.db_path}")
    
    def store_user_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Store or update a user profile.
        
        Args:
            profile_data: Complete user profile data
            
        Returns:
            bool: Success status
        """
        try:
            user_id = profile_data.get('user_id', self._generate_user_id(profile_data))
            profile_data['user_id'] = user_id  # Ensure user_id is in profile
            
            cursor = self.connection.cursor()
            
            # Check if user exists
            cursor.execute('SELECT user_id FROM user_profiles WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone() is not None
            
            experience_data = profile_data.get('experience', {})
            
            if exists:
                # Update existing profile
                cursor.execute('''
                    UPDATE user_profiles 
                    SET last_updated = ?, experience_years = ?, technical_field = ?, 
                        current_role = ?, skill_levels = ?, profile_data = ?
                    WHERE user_id = ?
                ''', (
                    datetime.now().isoformat(),
                    experience_data.get('years', 0),
                    experience_data.get('field', ''),
                    experience_data.get('current_role', ''),
                    json.dumps(experience_data.get('self_assessment', {})),
                    json.dumps(profile_data),
                    user_id
                ))
            else:
                # Insert new profile
                cursor.execute('''
                    INSERT INTO user_profiles 
                    (user_id, created_at, last_updated, experience_years, technical_field, 
                     current_role, skill_levels, profile_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    experience_data.get('years', 0),
                    experience_data.get('field', ''),
                    experience_data.get('current_role', ''),
                    json.dumps(experience_data.get('self_assessment', {})),
                    json.dumps(profile_data)
                ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error storing user profile: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile by ID.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dict containing user profile or None if not found
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                profile_data = json.loads(row['profile_data'])
                profile_data['db_metadata'] = {
                    'created_at': row['created_at'],
                    'last_updated': row['last_updated']
                }
                return profile_data
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving user profile: {e}")
            return None
    
    def store_session_initialization(self, session_data: Dict[str, Any]) -> bool:
        """
        Store session initialization data.
        
        Args:
            session_data: Session initialization data
            
        Returns:
            bool: Success status
        """
        try:
            session_id = session_data['session_id']
            user_profile = session_data.get('user_profile', {})
            target_job = user_profile.get('target_job', {})
            
            # Ensure user profile is stored first
            if user_profile:
                self.store_user_profile(user_profile)
            
            user_id = user_profile.get('user_id', session_id)  # Use session_id as fallback
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO sessions 
                (session_id, user_id, created_at, status, target_company, target_role, 
                 difficulty_level, session_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                user_id,
                session_data.get('created_at', datetime.now().isoformat()),
                session_data.get('status', 'initialized'),
                target_job.get('company', ''),
                target_job.get('role', ''),
                user_profile.get('difficulty_level', 'intermediate'),
                json.dumps(session_data)
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error storing session initialization: {e}")
            return False
    
    def store_session_record(self, session_record: Dict[str, Any]) -> bool:
        """
        Store complete session record with performance data.
        
        Args:
            session_record: Complete session record
            
        Returns:
            bool: Success status
        """
        try:
            session_id = session_record['session_id']
            user_profile = session_record.get('user_profile', {})
            user_id = user_profile.get('user_id', session_id)
            
            # Update session completion
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE sessions 
                SET completed_at = ?, status = 'completed', session_data = ?
                WHERE session_id = ?
            ''', (
                session_record['timestamp'],
                json.dumps(session_record),
                session_id
            ))
            
            # Store performance metrics
            performance_analysis = session_record.get('performance_analysis', {})
            category_scores = performance_analysis.get('category_scores', {})
            
            for category, score in category_scores.items():
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (session_id, user_id, recorded_at, category, metric_name, metric_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id, session_record['timestamp'], 
                    category, 'category_score', score
                ))
            
            # Store overall performance score
            overall_score = performance_analysis.get('overall_score', 0.0)
            cursor.execute('''
                INSERT INTO performance_metrics 
                (session_id, user_id, recorded_at, category, metric_name, metric_value)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id, user_id, session_record['timestamp'], 
                'overall', 'session_score', overall_score
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error storing session record: {e}")
            return False
    
    def store_completed_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Store completed session data.
        
        Args:
            session_data: Complete session data
            
        Returns:
            bool: Success status
        """
        return self.store_session_record(session_data)
    
    def get_performance_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get performance history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of session performance data
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT session_data FROM sessions 
                WHERE user_id = ? AND status = 'completed'
                ORDER BY completed_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            history = []
            
            for row in rows:
                session_data = json.loads(row['session_data'])
                history.append(session_data)
            
            return history
            
        except Exception as e:
            print(f"❌ Error retrieving performance history: {e}")
            return []
    
    def get_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Generate learning insights based on stored data.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing learning insights and recommendations
        """
        try:
            cursor = self.connection.cursor()
            
            # Get performance trends
            cursor.execute('''
                SELECT category, metric_value, recorded_at 
                FROM performance_metrics 
                WHERE user_id = ? AND metric_name = 'category_score'
                ORDER BY recorded_at ASC
            ''', (user_id,))
            
            metrics = cursor.fetchall()
            
            insights = {
                'user_id': user_id,
                'total_sessions': 0,
                'performance_trends': {},
                'improvement_areas': [],
                'strong_areas': [],
                'learning_velocity': 'moderate',
                'recommendations': []
            }
            
            if not metrics:
                return insights
            
            # Count total sessions
            cursor.execute('''
                SELECT COUNT(*) as session_count 
                FROM sessions 
                WHERE user_id = ? AND status = 'completed'
            ''', (user_id,))
            
            session_count = cursor.fetchone()['session_count']
            insights['total_sessions'] = session_count
            
            # Analyze performance trends by category
            category_performance = {}
            for metric in metrics:
                category = metric['category']
                score = metric['metric_value']
                
                if category not in category_performance:
                    category_performance[category] = []
                category_performance[category].append(score)
            
            # Calculate trends and identify areas
            for category, scores in category_performance.items():
                if len(scores) >= 2:
                    trend = scores[-1] - scores[0]  # Simple trend calculation
                    avg_score = sum(scores) / len(scores)
                    
                    insights['performance_trends'][category] = {
                        'current_score': scores[-1],
                        'average_score': avg_score,
                        'trend': 'improving' if trend > 0.1 else 'declining' if trend < -0.1 else 'stable',
                        'sessions_tracked': len(scores)
                    }
                    
                    # Categorize as strong or needs improvement
                    if avg_score >= 0.7:
                        insights['strong_areas'].append(category)
                    elif avg_score < 0.5:
                        insights['improvement_areas'].append(category)
            
            # Generate recommendations
            insights['recommendations'] = self._generate_learning_recommendations(insights)
            
            return insights
            
        except Exception as e:
            print(f"❌ Error generating learning insights: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields in user profile.
        
        Args:
            user_id: User identifier
            updates: Dictionary of fields to update
            
        Returns:
            bool: Success status
        """
        try:
            # Get current profile
            current_profile = self.get_user_profile(user_id)
            if not current_profile:
                return False
            
            # Apply updates
            current_profile.update(updates)
            current_profile['last_updated'] = datetime.now().isoformat()
            
            # Store updated profile
            return self.store_user_profile(current_profile)
            
        except Exception as e:
            print(f"❌ Error updating user profile: {e}")
            return False
    
    def store_question_performance(self, session_id: str, user_id: str, question_data: Dict, 
                                 response_data: Dict, scores: Dict[str, float]) -> bool:
        """
        Store individual question performance data.
        
        Args:
            session_id: Session identifier
            user_id: User identifier  
            question_data: Question details
            response_data: User response
            scores: Performance scores for the question
            
        Returns:
            bool: Success status
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO question_performance 
                (session_id, user_id, question_id, question_type, question_difficulty, topic_area,
                 response_time_seconds, accuracy_score, completeness_score, communication_score,
                 question_data, response_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                user_id,
                question_data.get('question_id', f"{session_id}_{len(question_data)}"),
                question_data.get('type', 'unknown'),
                question_data.get('difficulty', 'intermediate'),
                question_data.get('topic', 'general'),
                response_data.get('time_taken', 0),
                scores.get('accuracy_score', 0.0),
                scores.get('completeness_score', 0.0),
                scores.get('communication_score', 0.0),
                json.dumps(question_data),
                json.dumps(response_data)
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error storing question performance: {e}")
            return False
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing user statistics
        """
        try:
            cursor = self.connection.cursor()
            
            stats = {
                'user_id': user_id,
                'profile_created': '',
                'total_sessions': 0,
                'completed_sessions': 0,
                'total_questions_answered': 0,
                'average_session_score': 0.0,
                'best_session_score': 0.0,
                'recent_activity': '',
                'skill_progression': {},
                'time_invested_minutes': 0
            }
            
            # Basic profile info
            cursor.execute('SELECT created_at FROM user_profiles WHERE user_id = ?', (user_id,))
            profile_row = cursor.fetchone()
            if profile_row:
                stats['profile_created'] = profile_row['created_at']
            
            # Session statistics
            cursor.execute('''
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM sessions WHERE user_id = ?
            ''', (user_id,))
            session_stats = cursor.fetchone()
            stats['total_sessions'] = session_stats['total']
            stats['completed_sessions'] = session_stats['completed']
            
            # Performance statistics
            cursor.execute('''
                SELECT AVG(metric_value) as avg_score, MAX(metric_value) as best_score
                FROM performance_metrics 
                WHERE user_id = ? AND metric_name = 'session_score'
            ''', (user_id,))
            perf_stats = cursor.fetchone()
            if perf_stats['avg_score']:
                stats['average_session_score'] = round(perf_stats['avg_score'], 3)
                stats['best_session_score'] = round(perf_stats['best_score'], 3)
            
            # Questions answered
            cursor.execute('''
                SELECT COUNT(*) as question_count 
                FROM question_performance WHERE user_id = ?
            ''', (user_id,))
            q_stats = cursor.fetchone()
            stats['total_questions_answered'] = q_stats['question_count']
            
            # Recent activity
            cursor.execute('''
                SELECT MAX(completed_at) as last_session 
                FROM sessions WHERE user_id = ? AND status = 'completed'
            ''', (user_id,))
            recent = cursor.fetchone()
            if recent['last_session']:
                stats['recent_activity'] = recent['last_session']
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting user statistics: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
    def export_user_data(self, user_id: str, export_path: Optional[str] = None) -> str:
        """
        Export all user data to JSON file.
        
        Args:
            user_id: User identifier
            export_path: Optional custom export path
            
        Returns:
            str: Path to exported file
        """
        try:
            if export_path is None:
                export_dir = Path(__file__).parent / 'exports'
                export_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_path = export_dir / f"atic_export_{user_id}_{timestamp}.json"
            
            # Collect all user data
            export_data = {
                'export_metadata': {
                    'user_id': user_id,
                    'export_timestamp': datetime.now().isoformat(),
                    'export_version': '1.0'
                },
                'user_profile': self.get_user_profile(user_id),
                'performance_history': self.get_performance_history(user_id, limit=100),
                'learning_insights': self.get_learning_insights(user_id),
                'user_statistics': self.get_user_statistics(user_id)
            }
            
            # Write to file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            print(f"📤 User data exported to: {export_path}")
            return str(export_path)
            
        except Exception as e:
            print(f"❌ Error exporting user data: {e}")
            return ""
    
    def cleanup_old_data(self, days_old: int = 90) -> int:
        """
        Clean up old session data older than specified days.
        
        Args:
            days_old: Remove data older than this many days
            
        Returns:
            int: Number of records cleaned up
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            cursor = self.connection.cursor()
            
            # Delete old performance metrics
            cursor.execute('''
                DELETE FROM performance_metrics 
                WHERE recorded_at < ?
            ''', (cutoff_date,))
            
            deleted_metrics = cursor.rowcount
            
            # Delete old sessions (but keep user profiles)
            cursor.execute('''
                DELETE FROM sessions 
                WHERE created_at < ? AND status = 'completed'
            ''', (cutoff_date,))
            
            deleted_sessions = cursor.rowcount
            
            self.connection.commit()
            
            total_deleted = deleted_metrics + deleted_sessions
            print(f"🧹 Cleaned up {total_deleted} old records (>{days_old} days)")
            
            return total_deleted
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return 0
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("💾 Memory Bank connection closed")
    
    # Helper methods
    
    def _generate_user_id(self, profile_data: Dict[str, Any]) -> str:
        """Generate unique user ID based on profile data."""
        experience = profile_data.get('experience', {})
        field = experience.get('field', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"user_{field}_{timestamp}"
    
    def _generate_learning_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate learning recommendations based on insights."""
        recommendations = []
        
        improvement_areas = insights.get('improvement_areas', [])
        strong_areas = insights.get('strong_areas', [])
        total_sessions = insights.get('total_sessions', 0)
        
        # Recommendations based on improvement areas
        for area in improvement_areas[:3]:  # Top 3 areas needing work
            recommendations.append(f"Focus on improving {area.replace('_', ' ')} skills")
        
        # Recommendations based on session count
        if total_sessions < 3:
            recommendations.append("Complete more practice sessions to build momentum")
        elif total_sessions >= 5:
            recommendations.append("Consider tackling more advanced difficulty levels")
        
        # Recommendations based on strong areas
        if strong_areas:
            recommendations.append(f"Leverage your strength in {strong_areas[0].replace('_', ' ')} for complex problems")
        
        if not recommendations:
            recommendations.append("Continue regular practice to build and maintain skills")
        
        return recommendations
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()