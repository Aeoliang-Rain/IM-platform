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
import im.platform.client.ui.i18n.*
@Composable fun ConversationList(state:WorkspaceState,open:(String)->Unit){
    val t=useText()
LazyColumn(Modifier.fillMaxSize()){
            if(state.conversations.isEmpty())item{Panel(Modifier.fillMaxWidth(),state.appearance){Text(t("chat.next"),style=MaterialTheme.typography.titleLarge);Text(t("chat.addHint"))}}
            items(state.conversations,key={it}){id->Surface(onClick={open(id)},shape=RectangleShape,color=MaterialTheme.colorScheme.surface,modifier=Modifier.fillMaxWidth()){
                Column(Modifier.padding((16*state.appearance.density).dp)){Text(state.friends.find{it.directConversationId==id}?.user?.displayName?:t("chat.conversationId","id" to id.take(8)),fontWeight=FontWeight.SemiBold);Text(if(state.unavailable.contains(id))t("chat.access")else state.previews[id]?.text?.takeIf{it.isNotEmpty()}?:t("chat.noMessages"),maxLines=1,style=MaterialTheme.typography.bodyMedium)}
            }}
        }}
