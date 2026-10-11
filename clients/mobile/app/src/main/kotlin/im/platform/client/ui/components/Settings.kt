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
@OptIn(ExperimentalLayoutApi::class)
@Composable fun Settings(state:WorkspaceState,appearance:(Appearance)->Unit,disconnect:()->Unit,logout:()->Unit,reconnect:()->Unit,refresh:()->Unit){val p=state.appearance;Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(16.dp)){
    Panel(Modifier.fillMaxWidth(),p){Text("Appearance",style=MaterialTheme.typography.titleLarge);Text("Color, type and spacing are independent.",style=MaterialTheme.typography.bodyMedium);Row(verticalAlignment=Alignment.CenterVertically){Text("Theme",Modifier.weight(1f));TextButton(onClick={appearance(p.copy(theme=if(p.theme=="warm")"cold"else"warm"))}){Text(if(p.theme=="warm")"Warm Creative"else"Cold AI",fontSize=14.sp)}};Row(verticalAlignment=Alignment.CenterVertically){Text("Font size: ${p.fontSize}px",Modifier.weight(1f));OutlinedButton(onClick={appearance(p.copy(fontSize=p.fontSize-1))},enabled=p.fontSize>14){Text("−")};Spacer(Modifier.width(8.dp));OutlinedButton(onClick={appearance(p.copy(fontSize=p.fontSize+1))},enabled=p.fontSize<22){Text("+")}};Text("Spacing");FlowRow(horizontalArrangement=Arrangement.spacedBy(6.dp),verticalArrangement=Arrangement.spacedBy(4.dp)){listOf(.8f,1f,1.2f).forEachIndexed{i,d->FilterChip(selected=kotlin.math.abs(p.density-d)<.01f,onClick={appearance(p.copy(density=d))},label={Text(listOf("Compact","Standard","Comfort")[i],fontSize=12.sp)})}};Text("Saved on this device. Switching themes preserves type and spacing.",style=MaterialTheme.typography.bodyMedium)}
    ProfilePanel(state,disconnect,logout,reconnect,refresh)
}}
