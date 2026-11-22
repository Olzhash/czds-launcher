package app.czds.xash3d.launcher;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

/**
 * Лаунчер-мод для Xash3D FWGS. Повторяет механизм запуска оригинального клиента
 * CS 1.6 (in.celest.xash3d.cs16client v1.35), восстановленный из его байткода:
 *   Intent -> su.xash.engine[.test]/su.xash.engine.XashActivity
 *   extras: gamedir, gamelibdir, argv, package
 *
 * Отличия от оригинала (намеренные, см. COMPAT.md):
 *  - gamedir = czeror (оригинал: cstrike);
 *  - серверная библиотека без YaPB-ботов: -dll .../libserver.so (оригинал: libyapb.so);
 *  - добавлен -language russian: карты/модели лежат в czeror_russian;
 *  - перед запуском показывается предупреждение о несовместимости.
 */
public class MainActivity extends Activity {

    // ---- параметры запуска: единственное место, которое нужно править ----
    private static final String ENGINE_PKG_TEST = "su.xash.engine.test"; // как в оригинале: сначала test
    private static final String ENGINE_PKG_MAIN = "su.xash.engine";
    private static final String ENGINE_ACTIVITY = "su.xash.engine.XashActivity";
    private static final String GAMEDIR = "czeror";
    private static final String ENGINE_ARGS = "-dev 2 -log -language russian";
    private static final String GAME_DLL = "libserver.so";
    // -----------------------------------------------------------------------

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        final String enginePkg = findEngine();
        if (enginePkg == null) {
            openEngineStorePage();
            finish();
            return;
        }

        new AlertDialog.Builder(this)
                .setTitle(R.string.compat_title)
                .setMessage(R.string.compat_message)
                .setCancelable(false)
                .setPositiveButton(R.string.btn_launch, (d, w) -> launch(enginePkg))
                .setNegativeButton(R.string.btn_exit, (d, w) -> finish())
                .show();
    }

    private String findEngine() {
        PackageManager pm = getPackageManager();
        for (String pkg : new String[]{ENGINE_PKG_TEST, ENGINE_PKG_MAIN}) {
            try {
                pm.getPackageInfo(pkg, 0);
                return pkg;
            } catch (PackageManager.NameNotFoundException ignored) {
                // пробуем следующий
            }
        }
        return null;
    }

    private void launch(String enginePkg) {
        String libDir = getApplicationInfo().nativeLibraryDir;

        Intent i = new Intent();
        i.setComponent(new ComponentName(enginePkg, ENGINE_ACTIVITY));
        i.putExtra("gamedir", GAMEDIR);
        i.putExtra("gamelibdir", libDir);
        i.putExtra("argv", ENGINE_ARGS + " -dll " + libDir + "/" + GAME_DLL);
        i.putExtra("package", getPackageName());

        try {
            startActivity(i);
        } catch (ActivityNotFoundException | SecurityException e) {
            Toast.makeText(this, R.string.err_launch, Toast.LENGTH_LONG).show();
        }
        finish();
    }

    private void openEngineStorePage() {
        Toast.makeText(this, R.string.err_no_engine, Toast.LENGTH_LONG).show();
        try {
            Intent market = new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + ENGINE_PKG_MAIN));
            market.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(market);
        } catch (ActivityNotFoundException ignored) {
            // нет магазина приложений: пользователь ставит движок вручную
        }
    }
}
