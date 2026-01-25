package com.electricmayhem.robokart.controllerlibtesting;

import android.graphics.Color;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.TextView;

import com.electricmayhem.robokart.controllerlib.UniqueNameGenerator;
import com.electricmayhem.robokart.controllerlib.ZenohSessionManager;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import java.util.logging.Logger;

public class MainActivity extends AppCompatActivity {

    static Logger LOGGER = Logger.getLogger("MainActivity");

    private SeekBar turnControl;
    private SeekBar strafeControl;

    private Button forwardControl;
    private Button backwardControl;
    private Button initControl;

    private TextView statusView;
    private TextView connectionInfoView;

    private Toolbar toolbar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
//        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        turnControl = findViewById(R.id.turnControl);
        strafeControl = findViewById(R.id.strafeControl);
        forwardControl = findViewById(R.id.forwardControl);
        backwardControl = findViewById(R.id.backwardControl);
        initControl = findViewById(R.id.initControl);

        statusView = findViewById(R.id.statusView);
        connectionInfoView = findViewById(R.id.connectionInfoView);

        toolbar = findViewById(R.id.toolbar);

        initControl.setOnClickListener(v -> {
            ZenohSessionManager.initializeSession(this.getApplicationContext(), UniqueNameGenerator.generate());

            ZenohSessionManager.testUDP();

            statusView.setText(ZenohSessionManager.initSuccessful() ? "CONNECTED" : "ERROR");
            initControl.setText(ZenohSessionManager.initSuccessful() ? "REFRESH" : "RETRY");
            toolbar.setBackgroundColor(Color.parseColor(ZenohSessionManager.initSuccessful() ? "#00AA00" : "#AA0000"));
            connectionInfoView.setText(ZenohSessionManager.getConnInfoOrFailReason());
            LOGGER.info("New Connection Info: " + ZenohSessionManager.getConnInfoOrFailReason());
        });

        SeekBar.OnSeekBarChangeListener seekBarListener = new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                sendInputUpdate();
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                seekBar.setProgress(0);
            }
        };

        View.OnTouchListener buttonListener = (view, motionEvent) -> {
            view.performClick();
            if (motionEvent.getAction() == MotionEvent.ACTION_DOWN || motionEvent.getAction() == MotionEvent.ACTION_UP) {
                view.setPressed(motionEvent.getAction() == MotionEvent.ACTION_DOWN);
                view.setScaleX((float) (motionEvent.getAction() == MotionEvent.ACTION_DOWN ? 0.95 : 1));
                view.setScaleY((float) (motionEvent.getAction() == MotionEvent.ACTION_DOWN ? 0.95 : 1));
                sendInputUpdate();
                return true;
            }
            return false;
        };

        turnControl.setOnSeekBarChangeListener(seekBarListener);
        strafeControl.setOnSeekBarChangeListener(seekBarListener);
        forwardControl.setOnTouchListener(buttonListener);
        backwardControl.setOnTouchListener(buttonListener);

    }

    private void sendInputUpdate() {
        ZenohSessionManager.sendInput(
                turnControl.getProgress(),
                strafeControl.getProgress(),
                forwardControl.isPressed(),
                backwardControl.isPressed()
        );
    }

}