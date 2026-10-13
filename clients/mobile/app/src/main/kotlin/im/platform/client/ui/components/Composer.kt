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
@Composable fun Composer(state:WorkspaceState,draft:String,change:(String)->Unit,send:(String)->Unit,clear:()->Unit){
    val t=useText()
        Row(verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(8.dp)){OutlinedTextField(value=draft,onValueChange={if(it.codePointCount(0,it.length)<=4096)change(it)},label={Text(t("chat.message"))},modifier=Modifier.weight(1f),enabled=state.selected.isNotEmpty()&&state.session!=null,maxLines=3);Button(onClick={send(draft);clear()},enabled=state.selected.isNotEmpty()&&state.session!=null&&draft.isNotBlank()){Text(t("chat.send"))}}}
