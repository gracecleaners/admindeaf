# your_project/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

from accounts.models import User


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # Handle when a user disconnects
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data['user_id']
        is_online = data['is_online']
        await self.update_user_status(user_id, is_online)

    @database_sync_to_async
    def update_user_status(self, user_id, is_online):
        user = User.objects.get(pk=user_id)
        user.user_profile.is_online = is_online
        user.user_profile.save()

        # Notify all connected clients about the status change
        self.broadcast_user_status(user.id, is_online)

    async def broadcast_user_status(self, user_id, is_online):
        await self.send(text_data=json.dumps({
            'user_id': user_id,
            'is_online': is_online
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'public_room'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 'message': event['message'] }))


class UserNotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user_notification_id = None
        self.notification_group_id = None
        self.user = None

    async def connect(self):
        self.user = self.scope['user']
        print(self.user)
        self.user_notification_id = f'notification_inbox_{self.user.username}'
        await self.channel_layer.group_add(
            self.user_notification_id,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_notification_id,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 'message': event['message'] }))

class PaymentStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.payment_id = self.scope["url_route"]["kwargs"]["payment_id"]
        self.room_group_name = f"payment_{self.payment_id}"

        # Join the payment group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the payment group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def payment_status_update(self, event):
        # Send payment status update to WebSocket
        await self.send(text_data=json.dumps(event["data"]))


class RideMatchingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time ride matching updates"""
    
    async def connect(self):
        # Get user from scope (should be authenticated)
        self.user = self.scope['user']
        
        # Debug logging
        print(f"WebSocket connection attempt - User: {self.user}")
        print(f"User authenticated: {self.user.is_authenticated if self.user else 'No user'}")
        print(f"Session: {self.scope.get('session', {})}")
        
        if not self.user or not self.user.is_authenticated:
            print("WebSocket connection rejected - user not authenticated")
            await self.close()
            return
            
        # Create user-specific room group
        self.room_group_name = f"ride_matching_{self.user.id}"
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to ride matching updates',
            'user_id': self.user.id
        }))

    async def disconnect(self, close_code):
        # Leave the room group if it exists
        if hasattr(self, 'room_group_name') and self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_ride':
                # Subscribe to specific ride updates
                ride_request_id = data.get('ride_request_id')
                if ride_request_id:
                    await self.subscribe_to_ride(ride_request_id)
            elif message_type == 'driver_location_update':
                # Handle driver location updates
                await self.handle_driver_location_update(data.get('data', {}))
            elif message_type == 'driver_status_update':
                # Handle driver status updates
                await self.handle_driver_status_update(data.get('data', {}))
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON data'
            }))

    async def subscribe_to_ride(self, ride_request_id):
        """Subscribe to updates for a specific ride request"""
        ride_group_name = f"ride_request_{ride_request_id}"
        await self.channel_layer.group_add(
            ride_group_name,
            self.channel_name
        )
        
        await self.send(text_data=json.dumps({
            'type': 'subscribed',
            'message': f'Subscribed to ride request {ride_request_id}',
            'ride_request_id': ride_request_id
        }))

    # Event handlers for different types of ride matching updates
    async def ride_matching_update(self, event):
        """Send ride matching status update"""
        await self.send(text_data=json.dumps({
            'type': 'matching_update',
            'data': event['data']
        }))

    async def driver_response(self, event):
        """Send driver response update"""
        await self.send(text_data=json.dumps({
            'type': 'driver_response',
            'data': event['data']
        }))

    async def ride_confirmed(self, event):
        """Send ride confirmation update"""
        await self.send(text_data=json.dumps({
            'type': 'ride_confirmed',
            'data': event['data']
        }))

    async def ride_cancelled(self, event):
        """Send ride cancellation update"""
        await self.send(text_data=json.dumps({
            'type': 'ride_cancelled',
            'data': event['data']
        }))

    async def driver_timeout(self, event):
        """Send driver timeout notification"""
        await self.send(text_data=json.dumps({
            'type': 'driver_timeout',
            'data': event['data']
        }))

    async def next_driver_selected(self, event):
        """Send next driver selection update"""
        await self.send(text_data=json.dumps({
            'type': 'next_driver_selected',
            'data': event['data']
        }))

    async def driver_location_update(self, event):
        """Send driver location update"""
        await self.send(text_data=json.dumps({
            'type': 'driver_location_update',
            'data': event['data']
        }))

    async def driver_arrived(self, event):
        """Send driver arrived notification"""
        await self.send(text_data=json.dumps({
            'type': 'driver_arrived',
            'data': event['data']
        }))

    async def ride_started(self, event):
        """Send ride started notification"""
        await self.send(text_data=json.dumps({
            'type': 'ride_started',
            'data': event['data']
        }))

    async def ride_completed(self, event):
        """Send ride completed notification"""
        await self.send(text_data=json.dumps({
            'type': 'ride_completed',
            'data': event['data']
        }))

    async def ride_request(self, event):
        """Send ride request notification to driver"""
        await self.send(text_data=json.dumps({
            'type': 'ride_request',
            'data': event['data']
        }))

    async def driver_declined(self, event):
        """Send driver declined notification"""
        await self.send(text_data=json.dumps({
            'type': 'driver_declined',
            'data': event['data']
        }))

    async def handle_driver_location_update(self, data):
        """Handle driver location update from WebSocket"""
        try:
            ride_id = data.get('ride_id')
            if ride_id:
                # Get the ride_request_id from the ride_matching_id
                from rides.models import RideMatching
                try:
                    ride_matching = RideMatching.objects.get(id=ride_id)
                    ride_request_id = ride_matching.ride_request.id
                    
                    # Forward location update to ride-specific group using ride_request_id
                    await self.channel_layer.group_send(
                        f"ride_request_{ride_request_id}",
                        {
                            'type': 'driver_location_update',
                            'data': {
                                **data,
                                'ride_request_id': ride_request_id
                            }
                        }
                    )
                except RideMatching.DoesNotExist:
                    print(f"RideMatching with ID {ride_id} not found")
        except Exception as e:
            print(f"Error handling driver location update: {e}")

    async def handle_driver_status_update(self, data):
        """Handle driver status update from WebSocket"""
        try:
            ride_id = data.get('ride_id')
            status = data.get('status')
            
            if ride_id and status:
                # Get the ride_request_id from the ride_matching_id
                from rides.models import RideMatching
                try:
                    ride_matching = RideMatching.objects.get(id=ride_id)
                    ride_request_id = ride_matching.ride_request.id
                    
                    # Forward status update to ride-specific group using ride_request_id
                    await self.channel_layer.group_send(
                        f"ride_request_{ride_request_id}",
                        {
                            'type': f'driver_{status}',
                            'data': {
                                **data,
                                'ride_request_id': ride_request_id
                            }
                        }
                    )
                except RideMatching.DoesNotExist:
                    print(f"RideMatching with ID {ride_id} not found")
        except Exception as e:
            print(f"Error handling driver status update: {e}")