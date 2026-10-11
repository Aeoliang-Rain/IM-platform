package im.platform.client.ui.components
import androidx.compose.runtime.*
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.*

import im.platform.client.ui.*
@Composable fun ConversationList(state:WorkspaceState,open:(String)->Unit){LazyColumn(Modifier.fillMaxSize()){
            if(state.conversations.isEmpty())item{Panel(Modifier.fillMaxWidth(),state.appearance){Text("Your next conversation starts here",style=MaterialTheme.typography.titleLarge);Text("Find a friend to open a private chat.")}}
            items(state.conversations,key={it}){id->Surface(onClick={open(id)},shape=RectangleShape,color=MaterialTheme.colorScheme.surface,modifier=Modifier.fillMaxWidth()){
                Column(Modifier.padding((16*state.appearance.density).dp)){Text(state.friends.find{it.directConversationId==id}?.user?.displayName?:"Conversation "+id.take(8),fontWeight=FontWeight.SemiBold);Text(if(state.unavailable.contains(id))"Access unavailable"else state.previews[id]?.text?:"No messages yet",maxLines=1,style=MaterialTheme.typography.bodyMedium)}
            }}
        }}
