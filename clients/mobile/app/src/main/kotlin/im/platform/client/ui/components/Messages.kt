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
import androidx.compose.ui.unit.Dp
@Composable fun Messages(state:WorkspaceState,spacing:Dp,retry:(String)->Unit,modifier:Modifier){
    val t=useText()
LazyColumn(modifier.fillMaxWidth(),verticalArrangement=Arrangement.spacedBy(spacing)) {
            if(state.messages.isEmpty())item{Column(Modifier.fillMaxWidth().padding(35.dp),horizontalAlignment=Alignment.CenterHorizontally){Text(if(state.selected.isEmpty())t("chat.place")else t("chat.fresh"),style=MaterialTheme.typography.titleMedium);Text(if(state.selected.isEmpty())t("chat.choose")else t("chat.hello"),style=MaterialTheme.typography.bodyMedium)}}
            items(state.messages){m->val own=m[1]==(state.session?.userId?:state.offlineAccount);Column(Modifier.fillMaxWidth(),horizontalAlignment=if(own)Alignment.End else Alignment.Start){Surface(color=if(own)MaterialTheme.colorScheme.secondaryContainer else MaterialTheme.colorScheme.surface,shape=RoundedCornerShape(14.dp),modifier=Modifier.widthIn(max=310.dp)){Text(m[2]?:"",modifier=Modifier.padding((14*state.appearance.density).dp))};Row(verticalAlignment=Alignment.CenterVertically){Text(when(m[3]){"SENT"->t("chat.sent");"SENDING"->t("chat.sending");else->t("chat.failed")},style=MaterialTheme.typography.bodyMedium);if(own&&m[3]=="FAILED"&&m[0]!=null)TextButton(onClick={retry(m[0]!!)},enabled=state.session!=null){Text(t("chat.retry"))}}}}
        }}
