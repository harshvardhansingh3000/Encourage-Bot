import discord
from discord.ext import commands
import psycopg2
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

class BotDatabase:
    def __init__(self):
        load_dotenv()
        self.connection_params = {
            "dbname": os.getenv("POSTGRES_DB", "Encourage Bot"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASS"),
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432")
        }
    
    def get_connection(self):
        try:
            return psycopg2.connect(**self.connection_params)
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            raise
        
    def release_connection(self, connection):
        """
        Close the database connection
        
        :param connection: Database connection to close
        """
        try:
            if connection:
                connection.close()
        except psycopg2.Error as e:
            print(f"Error closing connection: {e}")

    def track_user_activity_patterns(self, user_id: int) -> Dict[str, Any]:
        """
        Analyzes user's activity patterns and returns insights about their behavior
        Returns peak activity hours, most used commands, and activity trends
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_activities (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        command TEXT,
                        timestamp TIMESTAMP
                    )
                """)
                
                # Get peak activity hours
                cur.execute("""
                    SELECT EXTRACT(HOUR FROM timestamp) as hour,
                           COUNT(*) as activity_count
                    FROM user_activities
                    WHERE user_id = %s
                    GROUP BY hour
                    ORDER BY activity_count DESC
                    LIMIT 3
                """, (user_id,))
                peak_hours = cur.fetchall()
                
                # Get most used commands
                cur.execute("""
                    SELECT command, COUNT(*) as usage_count
                    FROM user_activities
                    WHERE user_id = %s
                    GROUP BY command
                    ORDER BY usage_count DESC
                    LIMIT 5
                """, (user_id,))
                popular_commands = cur.fetchall()
                
                return {
                    "peak_hours": [{"hour": hour, "count": count} for hour, count in peak_hours],
                    "popular_commands": [{"command": cmd, "count": count} for cmd, count in popular_commands]
                }

    def implement_context_memory(self, user_id: int, context: str, max_memory: int = 10) -> List[str]:
        """
        Implements a conversation memory system that remembers previous contexts
        and allows for more natural conversations
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_memory (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        context TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Store new context
                cur.execute("""
                    INSERT INTO conversation_memory (user_id, context)
                    VALUES (%s, %s)
                """, (user_id, context))
                
                # Retrieve conversation history BEFORE cleaning up
                cur.execute("""
                    SELECT context FROM conversation_memory
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (user_id, max_memory))
                
                memory_list = [row[0] for row in cur.fetchall()]
                
                # Clean up old entries
                cur.execute("""
                    DELETE FROM conversation_memory
                    WHERE id NOT IN (
                        SELECT id FROM conversation_memory
                        WHERE user_id = %s
                        ORDER BY timestamp DESC
                        LIMIT %s
                    )
                    AND user_id = %s
                """, (user_id, max_memory, user_id))
                
                conn.commit()
                return memory_list

    def create_dynamic_user_rankings(self) -> List[Dict[str, Any]]:
        """
        Creates a dynamic ranking system based on user participation,
        helpfulness, and activity metrics
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create necessary tables if they don't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_points (
                        user_id BIGINT PRIMARY KEY,
                        activity_points INTEGER DEFAULT 0,
                        helpful_reactions INTEGER DEFAULT 0,
                        streak_days INTEGER DEFAULT 0,
                        last_active DATE
                    )
                """)
                
                # Calculate rankings with weighted scores
                cur.execute("""
                    SELECT 
                        user_id,
                        activity_points,
                        helpful_reactions,
                        streak_days,
                        (activity_points * 0.4 + helpful_reactions * 0.4 + streak_days * 0.2) as total_score
                    FROM user_points
                    ORDER BY total_score DESC
                    LIMIT 10
                """)
                
                rankings = cur.fetchall()
                return [
                    {
                        "user_id": r[0],
                        "activity_points": r[1],
                        "helpful_reactions": r[2],
                        "streak_days": r[3],
                        "total_score": r[4]
                    }
                    for r in rankings
                ]

    def implement_smart_reminders(self, user_id: int, reminder_text: str, context_based_delay: str) -> Dict[str, Any]:
        """
        Creates context-aware reminders that adjust timing based on user activity patterns
        and message context
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create reminders table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS smart_reminders (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        reminder_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        scheduled_for TIMESTAMP,
                        context TEXT,
                        status TEXT DEFAULT 'pending'
                    )
                """)
                
                # Analyze user activity patterns to determine best reminder time
                cur.execute("""
                    SELECT EXTRACT(HOUR FROM timestamp) as hour,
                           COUNT(*) as activity_count
                    FROM user_activities
                    WHERE user_id = %s
                    GROUP BY hour
                    ORDER BY activity_count DESC
                    LIMIT 1
                """, (user_id,))
                
                peak_hour = cur.fetchone()
                
                # Calculate reminder time based on context and activity
                base_delay = {
                    "urgent": timedelta(hours=1),
                    "today": timedelta(hours=3),
                    "tomorrow": timedelta(days=1),
                    "week": timedelta(days=7)
                }.get(context_based_delay, timedelta(days=1))
                
                reminder_time = datetime.now() + base_delay
                if peak_hour:
                    reminder_time = reminder_time.replace(hour=int(peak_hour[0]))
                
                # Store reminder
                cur.execute("""
                    INSERT INTO smart_reminders (user_id, reminder_text, scheduled_for, context)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, scheduled_for
                """, (user_id, reminder_text, reminder_time, context_based_delay))
                
                reminder_id, scheduled_time = cur.fetchone()
                conn.commit()
                
                return {
                    "reminder_id": reminder_id,
                    "scheduled_for": scheduled_time,
                    "text": reminder_text,
                    "context": context_based_delay
                }

    def create_automatic_content_categorization(self, content: str) -> Dict[str, Any]:
        """
        Automatically categorizes user content using keyword analysis and stores
        it for improved search and organization
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Create necessary tables
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS content_categories (
                        id SERIAL PRIMARY KEY,
                        content TEXT,
                        categories JSONB,
                        keywords TEXT[],
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Simple keyword-based categorization
                categories = []
                keywords = []
                
                # Example category rules (expand based on your needs)
                if any(word in content.lower() for word in ['help', 'question', 'how', 'what']):
                    categories.append('support')
                if any(word in content.lower() for word in ['bug', 'error', 'issue', 'problem']):
                    categories.append('bug-report')
                if any(word in content.lower() for word in ['feature', 'suggestion', 'idea']):
                    categories.append('feature-request')
                
                # Extract potential keywords (simple implementation)
                words = content.lower().split()
                keywords = [word for word in words if len(word) > 4][:5]  # Simple keyword extraction
                
                # Store categorized content
                cur.execute("""
                    INSERT INTO content_categories (content, categories, keywords)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (content, json.dumps({"categories": categories}), keywords))
                
                content_id = cur.fetchone()[0]
                conn.commit()
                
                return {
                    "content_id": content_id,
                    "categories": categories,
                    "keywords": keywords
                }
                
                

    def setup_conversation_table(self):
        """Setup the conversation history table"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS gpt_conversation_history (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        channel_id BIGINT,
                        message TEXT,
                        bot_response TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        context_used TEXT[]
                    )
                """)
                conn.commit()

    def store_conversation(self, user_id: int, channel_id: int, message: str, bot_response: str, context_used: list) -> None:
        """Store a conversation entry in the database"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO gpt_conversation_history 
                    (user_id, channel_id, message, bot_response, context_used)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, channel_id, message, bot_response, context_used))
                conn.commit()

    def get_recent_conversations(self, user_id: int, channel_id: int, limit: int = 5) -> list:
        """Retrieve recent conversations for context"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT message, bot_response
                    FROM gpt_conversation_history
                    WHERE user_id = %s AND channel_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (user_id, channel_id, limit))
                return cur.fetchall()

    def clear_user_history(self, user_id: int, channel_id: int) -> None:
        """Clear conversation history for a user in a specific channel"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM gpt_conversation_history
                    WHERE user_id = %s AND channel_id = %s
                """, (user_id, channel_id))
                conn.commit()
                
    def save_feedback(self, user, rating, feedback):
        """
        Check if feedback table exists, create if not, and then save feedback.

        :param user: Discord user (as string)
        :param rating: Rating value (1-10)
        :param feedback: Feedback text
        :return: True if successful, False otherwise
        """
        # Table creation query
        create_table_query = """
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 10),
            feedback_text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Feedback insertion query
        insert_query = """
        INSERT INTO feedback (user_id, rating, feedback_text) 
        VALUES (%s, %s, %s)
        """

        connection = None
        try:
            # Get database connection
            connection = self.get_connection()
            cursor = connection.cursor()

            # Ensure table exists
            cursor.execute(create_table_query)
            connection.commit()

            # Insert feedback
            cursor.execute(insert_query, (str(user), rating, feedback))
            connection.commit()
            return True

        except (Exception, psycopg2.Error) as error:
            print(f"Error in save_feedback: {error}")
            if connection:
                connection.rollback()
            return False

        finally:
            if connection:
                cursor.close()
                self.release_connection(connection)
                
    def get_feedback(self, limit=None):
        """ 
        Retrieve feedback from the database 
        :param limit: Optional limit on number of feedback entries to retrieve
        :return: List of feedback dictionaries 
        """
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if limit:
                query = """
                SELECT id, user_id, rating, feedback_text, timestamp 
                FROM feedback 
                ORDER BY timestamp DESC 
                LIMIT %s
                """
                cursor.execute(query, (limit,))
            else:
                query = """
                SELECT id, user_id, rating, feedback_text, timestamp 
                FROM feedback 
                ORDER BY timestamp DESC
                """
                cursor.execute(query)
            
            # Fetch column names
            columns = [desc[0] for desc in cursor.description]
            
            # Convert results to list of dictionaries
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        
        except (Exception, psycopg2.Error) as error:
            print(f"Error retrieving feedback: {error}")
            return []
        
        finally:
            if connection:
                cursor.close()
                self.release_connection(connection)
    
    def get_average_rating(self):
        """ 
        Calculate the average feedback rating 
        :return: Average rating or None if no ratings 
        """
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute('SELECT AVG(rating) as avg_rating FROM feedback')
            result = cursor.fetchone()
            
            return float(result[0]) if result[0] is not None else None
        
        except (Exception, psycopg2.Error) as error:
            print(f"Error calculating average rating: {error}")
            return None
        
        finally:
            if connection:
                cursor.close()
                self.release_connection(connection)

class CogDBMS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = BotDatabase()
        print("Database cog initialized!")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Database systems are operational!")

    @commands.command(name="dbstatus")
    @commands.has_permissions(administrator=True)
    async def db_status(self, ctx):
        """Check if the database connection is working"""
        try:
            with self.db.get_connection() as conn:
                await ctx.send("✅ Database connection successful!")
        except Exception as e:
            await ctx.send(f"❌ Database connection failed: {str(e)}")

    @commands.command()
    async def track_activity(self, ctx, member: discord.Member = None):
        """Track activity patterns for a user - example - !track_activity @User123"""
        try:
            user = member or ctx.author
            patterns = self.db.track_user_activity_patterns(user.id)
            
            embed = discord.Embed(title=f"Activity Patterns for {user.display_name}", color=discord.Color.blue())
            
            # Peak Hours
            peak_hours_str = "\n".join([f"Hour {data['hour']}: {data['count']} activities" 
                                      for data in patterns['peak_hours']])
            embed.add_field(name="Peak Activity Hours", value=peak_hours_str or "No data", inline=False)
            
            # Popular Commands
            commands_str = "\n".join([f"{cmd}: used {count} times" 
                                    for cmd, count in patterns['popular_commands']])
            embed.add_field(name="Most Used Commands", value=commands_str or "No data", inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error tracking activity: {str(e)}")

    @commands.command()
    async def remember_context(self, ctx, *, context: str):
        """Store a context in the bot's memory - example - !remember_context This is text"""
        try:
            memories = self.db.implement_context_memory(ctx.author.id, context)
            
            embed = discord.Embed(title="Memory Updated", color=discord.Color.green())
            embed.add_field(name="Latest Memories", 
                          value="\n".join(memories[:5]) or "No memories stored",
                          inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error storing memory: {str(e)}")

    @commands.command()
    async def show_rankings(self, ctx):
        """Display user rankings"""
        try:
            rankings = self.db.create_dynamic_user_rankings()
            
            embed = discord.Embed(title="User Rankings", color=discord.Color.gold())
            
            for i, rank in enumerate(rankings, 1):
                user = self.bot.get_user(rank['user_id'])
                username = user.display_name if user else f"User {rank['user_id']}"
                
                embed.add_field(
                    name=f"#{i} {username}",
                    value=f"Score: {rank['total_score']:.1f}\n"
                          f"Activity: {rank['activity_points']}\n"
                          f"Helpful: {rank['helpful_reactions']}\n"
                          f"Streak: {rank['streak_days']} days",
                    inline=True
                )
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error fetching rankings: {str(e)}")

    @commands.command()
    async def set_reminder(self, ctx, delay: str, *, reminder_text: str):
        """Set a smart reminder
        Delay can be: urgent, today, tomorrow, week
        example - @set_reminder today I have appointment"""
        try:
            if delay not in ["urgent", "today", "tomorrow", "week"]:
                await ctx.send("Invalid delay! Use: urgent, today, tomorrow, or week")
                return
            
            reminder = self.db.implement_smart_reminders(
                ctx.author.id, 
                reminder_text,
                delay
            )
            
            embed = discord.Embed(title="Reminder Set", color=discord.Color.blue())
            embed.add_field(name="Text", value=reminder['text'], inline=False)
            embed.add_field(name="When", value=reminder['scheduled_for'].strftime('%Y-%m-%d %H:%M:%S'))
            embed.add_field(name="Type", value=reminder['context'])
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error setting reminder: {str(e)}")

    @commands.command()
    async def categorize_message(self, ctx, *, content: str):
        """Categorize a message's content - example - !categorize_message Hello there is a bug in the x command"""
        try:
            result = self.db.create_automatic_content_categorization(content)
            
            embed = discord.Embed(title="Content Categorization", color=discord.Color.purple())
            embed.add_field(name="Categories", 
                          value="\n".join(result['categories']) or "No categories found",
                          inline=False)
            embed.add_field(name="Keywords", 
                          value=", ".join(result['keywords']) or "No keywords extracted",
                          inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error categorizing content: {str(e)}")
    
    @commands.command()
    async def clear_context(self,ctx):
        """Clear conversation history for the user"""
        try:
            self.db.clear_user_history(ctx.author.id, ctx.channel.id)
            await ctx.send("Your conversation history has been cleared!")
        except Exception as e:
            await ctx.send("Failed to clear conversation history.")
            print(f"Error clearing history: {e}")

    @commands.command()
    async def show_context(self,ctx, limit: int = 5):
        """Show recent conversation history
        example - !show_context 10"""
        try:
            conversations = self.db.get_recent_conversations(
                ctx.author.id,
                ctx.channel.id,
                limit
            )
            
            if not conversations:
                await ctx.send("No conversation history found.")
                return
                
            embed = discord.Embed(title="Recent Conversations", color=discord.Color.blue())
            for i, (msg, response) in enumerate(conversations, 1):
                embed.add_field(
                    name=f"Conversation {i}",
                    value=f"You: {msg[:100]}...\nBot: {response[:100]}...",
                    inline=False
                )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("Failed to retrieve conversation history.")
            print(f"Error showing history: {e}")
            
    @commands.command()
    async def avg_rating(self, ctx):
        """Get the average feedback rating"""
        try:
            avg_rating = self.db.get_average_rating()
            
            if avg_rating is not None:
                embed = discord.Embed(
                    title="Average Feedback Rating", 
                    description=f"⭐ {avg_rating:.2f} / 10", 
                    color=discord.Color.gold()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("No ratings have been recorded yet.")
        except Exception as e:
            await ctx.send(f"Error retrieving average rating: {str(e)}")

    @commands.command()
    async def recent_feedback(self, ctx, limit: int = 5):
        """Show recent feedback entries
        example - !recent_feedback 10"""
        try:
            feedbacks = self.db.get_feedback(limit)
            
            if not feedbacks:
                await ctx.send("No feedback found.")
                return
            
            embed = discord.Embed(title="Recent Feedback", color=discord.Color.blue())
            for feedback in feedbacks:
                embed.add_field(
                    name=f"User {feedback['user_id']} (Rating: {feedback['rating']}/10)",
                    value=feedback['feedback_text'][:100] + "...",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error retrieving feedback: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(CogDBMS(bot))
