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
@OptIn(ExperimentalLayoutApi::class)
@Composable fun ProfilePanel(state:WorkspaceState,disconnect:()->Unit,logout:()->Unit,reconnect:()->Unit,refresh:()->Unit){
    val t=useText()
val p=state.appearance;    Panel(Modifier.fillMaxWidth(),p){Text(t("profile.session"),style=MaterialTheme.typography.titleLarge);Text(state.profile?.displayName?:t("profile.unavailable"),fontWeight=FontWeight.SemiBold);Text(state.profile?.let{"@"+it.username}?:(if(state.session!=null)t("profile.reconnect")else t("profile.signIn")));FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){OutlinedButton(onClick=refresh,enabled=!state.busy&&(state.session!=null||state.offlineAccount!=null)){Text(t("auth.refresh"))};OutlinedButton(onClick=disconnect,enabled=state.session!=null){Text(t("auth.offline"))}};FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){OutlinedButton(onClick=reconnect,enabled=state.session!=null){Text(t("auth.reconnect"))};Button(onClick=logout,enabled=!state.busy&&(state.session!=null||state.offlineAccount!=null)){Text(t("auth.signOut"))}}}}
