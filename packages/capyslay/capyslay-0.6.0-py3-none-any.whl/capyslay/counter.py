def counter():
    return [
        """
        <?xml version="1.0" encoding="utf-8"?>
        <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:orientation="vertical"
            android:gravity="center"
            android:padding="20dp">

            <TextView
                android:id="@+id/titleText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="COUNTER APPLICATION"
                android:textSize="20sp"
                android:textStyle="bold"
                android:paddingBottom="20dp"/>

            <TextView
                android:id="@+id/counterText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Counter Value: 0"
                android:textSize="18sp"
                android:paddingBottom="20dp"/>

            <Button
                android:id="@+id/startButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="START"/>

            <Button
                android:id="@+id/stopButton"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="STOP"
                android:layout_marginTop="10dp"/>

        </LinearLayout>
        """,
        """
        package com.example.program6counter;

        import android.os.Bundle;
        import android.os.Handler;
        import android.view.View;
        import android.widget.Button;

        import android.widget.TextView;
        import androidx.appcompat.app.AppCompatActivity;

        public class MainActivity extends AppCompatActivity {

            private TextView counterText;
            private Button startButton, stopButton;
            private int counter = 0;
            private Handler handler = new Handler();
            private boolean isCounting = false;

            private Runnable counterRunnable = new Runnable() {
                @Override
                public void run() {
                    if (isCounting) {
                        counter++;
                        counterText.setText("Counter Value: " + counter);
                        handler.postDelayed(this, 1000); // Repeat every 1 second
                    }
                }
            };

            @Override
            protected void onCreate(Bundle savedInstanceState) {
                super.onCreate(savedInstanceState);
                setContentView(R.layout.activity_main);

                counterText = findViewById(R.id.counterText);
                startButton = findViewById(R.id.startButton);
                stopButton = findViewById(R.id.stopButton);

                startButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        if (!isCounting) {
                            isCounting = true;
                            handler.post(counterRunnable);
                        }
                    }
                });

                stopButton.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        isCounting = false;
                        handler.removeCallbacks(counterRunnable);
                    }
                });
            }
        }
        """
    ]